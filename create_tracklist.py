from struct import pack  # imported in the current file but not used by the tracklist logic
import tkinter as tk  # import Tkinter for the tracklist GUI
from tkinter import ttk  # import ttk widgets for the interface
import csv  # read and write tracklist CSV files
from pathlib import Path  # handle file paths safely
import random  # shuffle the current tracklist order
import font_manager as font  # import theme and font helpers
import track_library_oop as lib  # import the shared track library
import pygame  # import pygame for audio playback
from tkinter import messagebox  # show duplicate-track confirmation dialogs



class CreateTracklist:
    # Tracklist manager window for building and controlling playlists.
    def __init__(self, window, library = None, theme_mode = "System"):
        self.window = window  # store the Tk window for the tracklist manager
        self.window.title("Create Tracklist")  # set the window title
        self.window.geometry("1300x850")  # set the default window size
        self.library = library or lib.TrackLibrary()  # use the shared library if one was passed in
        self.track_input = tk.StringVar()  # store the track number input
        self.tracklist_position = tk.StringVar()  # store the visible track position input
        self.tracklist = []  # store the current tracklist entries
        self.status_text = tk.StringVar(value = "Please insert track number to add tracks to your tracklist")  # show the initial help message
        self.tracklist_file = Path(__file__).with_name("saved_tracklist.csv")  # store the CSV file used for saving tracklists
        self.custom_track_name = tk.StringVar()  # store the custom track name input
        self.custom_track_artist = tk.StringVar()  # store the custom track artist input
        self.custom_track_path = tk.StringVar()  # store the custom track file path input
        self.current_index = -1  # store the current index in the tracklist
        self.is_playing = False  # track whether playback is active
        self.is_paused = False  # track whether playback is paused
        self.is_seeking = False  # track whether the user is dragging the progress slider
        self.after_id = None  # store the Tk timer ID for end-of-track checks
        self.playback_id = 0  # track the current playback session ID
        self.checking = False  # track whether the end-of-track checker is active
        self.theme_mode = theme_mode  # remember the selected theme mode
        self.tracklist_step = 1  # store the playback direction through the tracklist
        self.tracklist_loop = False  # track whether the full tracklist loops
        self.tracklist_playing = False  # track whether tracklist mode is active
        self.looped_positions = set()  # store tracklist positions that should loop
        self.looped_track_numbers = set()  # store track numbers that should loop

        self.playback_mode = None  # store whether single-track or tracklist playback is active
        self.current_track_number = None  # store the active track number
        self.progress_after_id = None  # store the timer ID for progress updates
        self.progress_value = tk.DoubleVar(value = 0)  # store the slider position as a Tk variable
        self.progress_text = tk.StringVar(value = "00:00 / 00:00")  # store the progress time label
        self.current_track_length = 0.0  # cache the active track length
        self.current_track_offset = 0.0  # cache the current seek offset
        

        controls = ttk.Frame(window, padding = 10)  # create the top control container
        controls.pack(fill = "x")  # stretch the controls across the window

        main_area = ttk.Frame(window, padding = (10, 0, 10, 0))  # create the main display area
        main_area.pack(side = "top", fill = "both", expand = True)  # let the main area expand

        self.tracklist_text = tk.Text(main_area, height = 18, width = 102, bg = "#31384a", fg = "#e7eaf0", insertbackground = "#e7eaf0", selectbackground = "#5f8fbe")  # text widget for the current tracklist
        self.tracklist_text.pack(fill = "both", expand = True)  # fill the main area with the tracklist view
        self.set_text(self.tracklist_text, "")  # start with an empty tracklist panel
        self.load_tracklist(auto_load = True)  # automatically restore any saved tracklist

        




        track_frame = ttk.LabelFrame(controls, text = "Track Actions", padding = 8)  # section for track add/play/remove actions
        track_frame.grid(row = 0, column = 0, sticky = "ew", padx = 4, pady = 4)  # place the track actions section
        ttk.Label(track_frame, text = "Track Number").grid(row = 0, column = 0, sticky = "w", padx = (0, 6))  # label the track number field
        ttk.Entry(track_frame, width = 8, textvariable = self.track_input).grid(row = 0, column = 1, padx = (0, 10))  # input box for track number
        ttk.Button(track_frame, text = "Add Track", command = self.add_track).grid(row = 0, column = 2, padx = 4)  # add track button
        ttk.Button(track_frame, text = "Play", command = self.play_track).grid(row = 0, column = 3, padx = 4)  # play track button
        ttk.Button(track_frame, text = "Remove", command = self.remove_track).grid(row = 0, column = 4, padx = 4)  # remove track button

        position_frame = ttk.LabelFrame(controls, text = "Track Position", padding = 8)  # section for playing by visible position
        position_frame.grid(row = 0, column = 1, sticky = "ew", padx = 4, pady = 4)  # place the position controls
        ttk.Label(position_frame, text = "Position").grid(row = 0, column = 0, sticky = "w", padx = (0, 6))  # label the position field
        ttk.Entry(position_frame, width = 8, textvariable = self.tracklist_position).grid(row = 0, column = 1, padx = (0, 10))  # input for tracklist position
        ttk.Button(position_frame, text = "Play Position", command = self.play_specific_track).grid(row = 0, column = 2, padx = 4)  # play the selected position

        
        custom_frame = ttk.LabelFrame(controls, text = "Custom Track", padding = 8)  # section for adding external audio files
        custom_frame.grid(row = 2, column = 0, columnspan = 2, sticky = "ew", padx = 4, pady = 4)  # place the custom track section
        ttk.Label(custom_frame, text = "Name").grid(row = 0, column = 0, sticky = "w", padx = (0, 6))  # label the custom track name field
        ttk.Entry(custom_frame, width = 20, textvariable = self.custom_track_name).grid(row = 0, column = 1, padx = (0, 10))  # input for custom track name
        ttk.Label(custom_frame, text = "Artist").grid(row = 0, column = 2, sticky = "w", padx = (0, 6))  # label the custom artist field
        ttk.Entry(custom_frame, width = 20, textvariable = self.custom_track_artist).grid(row = 0, column = 3, padx = (0, 10))  # input for custom artist
        ttk.Label(custom_frame, text = "Path").grid(row = 1, column = 0, sticky = "w", padx = (0, 6), pady = (8, 0))  # label the file path field
        ttk.Entry(custom_frame, width = 48, textvariable = self.custom_track_path).grid(row = 1, column = 1, columnspan = 3, sticky = "ew", padx = (0, 10), pady = (8, 0))  # input for audio path
        ttk.Button(custom_frame, text = "Add Custom Track", command = self.add_custom_track).grid(row = 1, column = 4, padx = 4, pady = (8, 0))  # add custom track button

        library_frame = ttk.LabelFrame(controls, text = "Tracklist Management", padding = 8)  # section for tracklist-wide management actions
        library_frame.grid(row = 3, column = 0, columnspan = 2, sticky = "ew", padx = 4, pady = 4)  # place the management section
        ttk.Button(library_frame, text = "Shuffle", command = self.shuffle_tracklist).grid(row = 0, column = 0, padx = 4)  # shuffle the tracklist order
        ttk.Button(library_frame, text = "Reset", command = self.reset_tracklist).grid(row = 0, column = 1, padx = 4)  # clear the tracklist
        ttk.Button(library_frame, text = "Save", command = self.save_tracklist).grid(row = 0, column = 2, padx = 4)  # save the current tracklist
        ttk.Button(library_frame, text = "Load", command = self.load_tracklist).grid(row = 0, column = 3, padx = 4)  # reload a saved tracklist

        bottom_bar = ttk.Frame(window, padding = 10)  # create the bottom control area
        bottom_bar.pack(side = "bottom", fill = "x")  # stretch the bottom bar across the window

        playback_frame = ttk.LabelFrame(bottom_bar, text = "Playback", padding = 8)  # section for playback controls
        playback_frame.pack(fill = "x", pady = (0, 6))  # place the playback section at the bottom

        self.play_stop_button = ttk.Button(playback_frame, text = "Play / Stop tracklist", command = self.toggle_play_stop)  # start or stop the tracklist
        self.play_stop_button.grid(row = 0, column = 0, padx = 4)  # place the play/stop button
        self.pause_resume_button = ttk.Button(playback_frame, text = "Pause / Resume", command = self.toggle_pause_resume)  # pause or resume playback
        self.pause_resume_button.grid(row = 0, column = 1, padx = 4)  # place the pause/resume button
        ttk.Button(playback_frame, text = "Skip", command = self.skip_track).grid(row = 0, column = 2, padx = 4)  # skip forward
        ttk.Button(playback_frame, text = "Reverse", command = self.reverse_track).grid(row = 0, column = 3, padx = 4)  # move backward
        self.loop_button = ttk.Button(playback_frame, text = "Loop Tracklist", command = self.toggle_tracklist_loop_ui)  # toggle full tracklist looping
        self.loop_button.grid(row = 0, column = 4, padx = 4)  # place the loop button
        self.loop_track_button = ttk.Button(playback_frame, text = "Loop Selected Track", command = self.toggle_selected_track_loop)  # toggle looping by visible position
        self.loop_track_button.grid(row = 0, column = 5, padx = 4)  # place the selected-track loop button
        self.loop_track_number_button = ttk.Button(playback_frame, text = "Loop Track Number", command = self.toggle_selected_track_number_loop)  # toggle looping by track number
        self.loop_track_number_button.grid(row = 0, column = 6, padx = 4)  # place the track-number loop button

        progress_frame = ttk.Frame(window, padding = (10, 0, 10, 0))  # create the progress bar container
        progress_frame.pack(fill = "x")  # stretch the progress area across the window

        self.progress_bar = tk.Scale(progress_frame, from_ = 0, to = 100, orient = "horizontal", showvalue = False, resolution = 0.1, variable = self.progress_value, length = 500, command = self._seek_change)  # draggable seek slider
        self.progress_bar.pack(fill = "x")  # stretch the slider horizontally

        self.progress_bar.bind("<ButtonPress-1>", self._begin_seek)  # mark the start of a seek action
        self.progress_bar.bind("<ButtonRelease-1>", self._end_seek)  # perform the seek when the slider is released

        ttk.Label(progress_frame, textvariable = self.progress_text).pack(anchor = "e")  # show the current time label

        ttk.Label(bottom_bar, textvariable = self.status_text, padding = (10, 8)).pack(fill = "x")  # show status messages at the bottom

        if self.theme_mode == "System":  # if system theme is selected
            font.apply_device_theme(self.window)  # apply the OS theme
        else:
            font.apply_theme(self.window, self.theme_mode)  # apply the selected custom theme
        
        self._update_progress_bar()  # start the repeating progress update loop
        
    # Replace the contents of a text widget with new text.
    def set_text(self, text_area, content):
        text_area.configure(state = "normal")  # unlock the text box before replacing its content
        text_area.delete("1.0", tk.END)  # remove everything currently in the widget
        text_area.insert("1.0", content)  # insert the new text at the top
        text_area.configure(state = "disabled")  # lock the widget again so it is display-only

    # Format the current tracklist for display in the text panel.
    def _format_tracklist(self):
        lines = []  # collect each display line here
        for index, track_number in enumerate(self.tracklist):  # loop through every track in the list
            name = self.library.get_name(track_number) or "Unknown"  # get the track name or fall back to Unknown
            artist = self.library.get_artist(track_number)  # get the artist name if available
            if artist:  # if the artist exists
                lines.append(f"{index + 1}. {name} - {artist} ({track_number})")  # show name, artist, and track number
            else:
                lines.append(f"{index + 1}. {name} ({track_number})")  # show only the name if no artist exists
        return "\n".join(lines)  # join all lines into one text block
    
    # Convert seconds into mm:ss format for the progress label.
    def _format_time(self, seconds):
        seconds = max(0, int(seconds))  # clamp negative values to zero and remove decimals
        return f"{seconds // 60:02d}:{seconds % 60:02d}"  # format seconds as mm:ss
    
    # Refresh the progress slider and time label from the current playback position.
    def _update_progress_bar(self):
        try:
            if self.current_track_number is None or self.current_track_length <= 0:  # if no track is active
                self.progress_value.set(0)  # reset the slider
                self.progress_text.set("00:00 / 00:00")  # reset the time label
            elif self.is_playing or self.is_paused:  # if playback is active or paused
                if not self.is_seeking:  # do not overwrite the slider while the user is dragging it
                    pos_ms = pygame.mixer.music.get_pos()  # read the current playback position from pygame
                    if pos_ms < 0:  # handle invalid mixer values
                        elapsed = self.current_track_offset  # fall back to the saved offset
                    else:
                        elapsed = min(self.current_track_offset + (pos_ms / 1000.0), self.current_track_length)  # calculate elapsed time

                    percent = (elapsed / self.current_track_length) * 100  # convert elapsed time to a percentage
                    self.progress_value.set(percent)  # update the slider position
                    self.progress_text.set(f"{self._format_time(elapsed)} / {self._format_time(self.current_track_length)}")  # update the label

            else:
                self.progress_value.set(0)  # reset the slider when nothing is playing
                self.progress_text.set("00:00 / 00:00")  # reset the time label

        except Exception:
            self.progress_value.set(0)  # fall back to zero on any error
            self.progress_text.set("00:00 / 00:00")  # fall back to the default label

        self.progress_after_id = self.window.after(250, self._update_progress_bar)  # schedule the next refresh



    def _begin_seek(self, event = None):
        self.is_seeking = True  # prevent the automatic updater from overwriting the drag
    
    def _end_seek(self, event = None):
        if self.current_track_number is None or self.current_track_length <= 0:  # reject invalid seek attempts
            self.is_seeking = False  # clear the seeking flag
            return
        
        seek_percent = float(self.progress_value.get())  # read the slider position
        seek_seconds = (seek_percent / 100.0) * self.current_track_length  # convert the slider percentage into seconds

        if self.playback_mode == "tracklist" and 0 <= self.current_index < len(self.tracklist):  # if tracklist playback is active
            track_number = self.tracklist[self.current_index]  # seek the current tracklist item
            looping = self._is_looped_track(self.current_index)  # check whether the current item loops
        elif self.playback_mode == "single":  # if single-track playback is active
            track_number = self.current_track_number  # seek the active single track
            looping = self.current_track_number in self.looped_track_numbers  # check whether that track is looped
        else:
            self.is_seeking = False  # clear the seeking flag
            return
        
        self.playback_id += 1  # bump the playback session ID so old timers are ignored
        self._stop_current_playback()  # stop the current audio before restarting it
        self.is_playing = True  # mark playback active again
        self.is_paused = False  # clear paused state
        self.checking = True  # re-enable the end-of-track checker

        if self.library.play_track(track_number, loop = looping, start_seconds = seek_seconds):  # restart playback from the chosen position
            self.current_track_number = track_number  # store the active track number
            self.current_track_length = self.library.get_track_length(track_number)  # refresh the track length cache
            self.current_track_offset = seek_seconds  # store the chosen offset
            self.status_text.set(f"Seeked to {self._format_time(seek_seconds)}.")  # confirm the seek
        else:
            self.status_text.set("Error occurred. Please try again.")  # show an error if seeking failed

        self.is_seeking = False  # allow automatic updates again



    def _seek_change(self, value):
        if self.current_track_length <= 0:  # ignore if there is no active track
            return
        try:
            seek_percent = float(value)  # convert the slider value into a number
        except(TypeError, ValueError):
            return
        
        seek_seconds = (seek_percent / 100.0) * self.current_track_length  # convert slider position into seconds
        self.progress_text.set(f"{self._format_time(seek_seconds)} / {self._format_time(self.current_track_length)}")  # preview the selected time





    # Refresh the visible tracklist text after a change.
    def _refresh_tracklist_text(self):
        self.set_text(self.tracklist_text, self._format_tracklist())  # redraw the tracklist text box

    # Add a track from the shared library by track number.
    def add_track(self):
        raw = self.track_input.get().strip()  # read the track number field
        track_number = raw.zfill(2) if raw.isdigit() else raw  # normalize numeric track numbers
        
        name = self.library.get_name(track_number)  # look up the track name
        if not name:  # reject invalid tracks
            self.status_text.set("Invalid track number, please enter a valid track number.")  # show an error message
            return
        
        if track_number in self.tracklist:  # if the track already exists in the list
            confirm = messagebox.askyesno("Duplicate track", f"'{name}' is already in your tracklist.\n\ Add it anyway?")  # ask whether to add a duplicate
            if not confirm:  # cancel if the user says no
                self.status_text.set("Track is not added.")  # tell the user nothing was added
                return
            

        self.tracklist.append(track_number)  # append the track to the list
        self._refresh_tracklist_text()  # redraw the visible tracklist
        self.status_text.set(f"Added '{name}' to tracklist.")  # confirm the add

    # Add a custom audio file to the library and insert it into the tracklist.
    def add_custom_track(self):
        custom_name = self.custom_track_name.get().strip()  # read the custom track name
        custom_artist = self.custom_track_artist.get().strip()  # read the custom track artist
        custom_path = self.custom_track_path.get().strip()  # read the custom audio path

        if not custom_name:  # require a custom track name
            self.status_text.set("Please enter a custom track name.")  # prompt the user
            return

        if not custom_artist:  # require a custom artist
            self.status_text.set("Please enter a custom artist.")  # prompt the user
            return

        if not custom_path:  # require a file path
            self.status_text.set("Please enter the audio file path.")  # prompt the user
            return

        if not Path(custom_path).exists():  # check that the audio file exists
            self.status_text.set("Audio file not found at that path.")  # show an error
            return

        custom_track_id = self._next_custom_track_id()  # generate a unique custom track ID
        self.library.add_custom_track(custom_track_id, custom_name, custom_artist, custom_path)  # add it to the shared library
        self.tracklist.append(custom_track_id)  # add it to the current tracklist
        self._refresh_tracklist_text()  # redraw the visible tracklist
        self.custom_track_name.set("")  # clear the name field
        self.custom_track_artist.set("")  # clear the artist field
        self.custom_track_path.set("")  # clear the path field
        self.status_text.set(f"Added custom track '{custom_name}' to tracklist.")  # confirm the addition

    # Start playback of the saved tracklist.
    def play_tracklist(self):
        if not self.tracklist:  # reject empty tracklists
            self.status_text.set("List is empty. Please add some tracks in.")  # tell the user to add tracks
            return
        
        self.stop_playback()  # stop any current playback first
        self.playback_id += 1  # advance the playback session ID
        self.current_index = -1  # reset the active index
        self.tracklist_step = 1  # start playback moving forward
        self.is_playing = True  # mark playback active
        self.is_paused = False  # clear paused state
        self.checking = True  # enable end-of-track checking
        self.tracklist_playing = True  # mark tracklist playback as active

        if getattr(self, "play_stop_button", None) is not None:  # if the play/stop button exists
            self.play_stop_button.configure(text = "Stop Tracklist")  # switch the label to stop mode
        if getattr(self, "pause_resume_button", None) is not None:  # if the pause/resume button exists
            self.pause_resume_button.configure(text = "Pause")  # switch the label to pause mode
        
        self._play_next_in_tracklist(self.playback_id)  # start playback of the first track


    # Stop playback if active, otherwise start tracklist playback.
    def toggle_play_stop(self):
        if self.tracklist_playing or self.is_playing or self.is_paused:  # if playback is already active
            self.stop_playback()  # stop it
        else:
            self.play_tracklist()  # otherwise start playback
            self.play_stop_button.configure(text = "Stop Tracklist")  # update the button label
            self.pause_resume_button.configure(text = "Pause")  # reset the pause label
    
    # Pause or resume tracklist playback.
    def toggle_pause_resume(self):
        if self.is_paused:  # if playback is paused
            self.resume_playback()  # resume it
            self.pause_resume_button.configure(text = "Pause")  # update the button label
        else:
            self.pause_playback()  # pause playback
            self.pause_resume_button.configure(text = "Resume")  # update the button label
    
    # Toggle looping for the full tracklist.
    def toggle_tracklist_loop(self):
        self.tracklist_loop = not self.tracklist_loop  # flip the loop flag
        return self.tracklist_loop  # return the new state
    
    # Toggle looping for one selected tracklist position.
    def toggle_selected_track_loop(self):
        index = self._get_selected_tracklist_index()  # read the selected visible position
        if index is None:  # reject invalid input
            self.status_text.set("Please enter the position of the track.")  # prompt the user
            return
        
        if index in self.looped_positions:  # if the position is already looped
            self.looped_positions.remove(index)  # remove the loop marker
            self.status_text.set(f"Loop disabled for track {index + 1}.")  # confirm the change
        else:
            self.looped_positions.add(index)  # add the loop marker
            self.status_text.set(f"Loop enabled for track {index + 1}.")  # confirm the change
    
    # Toggle looping for a track selected by track number.
    def toggle_selected_track_number_loop(self):
        raw_track = self.track_input.get().strip()  # read the track number field
        track_number = self._normalize_track_number_input(raw_track)  # normalize the input

        if not track_number:  # reject empty input
            self.status_text.set("Please enter a track number.")  # prompt the user
            return
        
        if track_number not in self.library.library:  # reject tracks not in the library
            self.status_text.set("Track not found.")  # show an error
            return
        
        if track_number in self.looped_track_numbers:  # if the track is already looped
            self.looped_track_numbers.remove(track_number)  # remove the loop marker
            self.status_text.set(f"Loop disabled for track: {track_number}.")  # confirm the change
        else:
            self.looped_track_numbers.add(track_number)  # add the loop marker
            self.status_text.set(f"Loop enabled for track: {track_number}.")  # confirm the change
        




    # Advance to the next playable track in the current direction.
    def _play_next_in_tracklist(self, playback_id):
        if playback_id != self.playback_id or not self.is_playing:  # ignore stale timer events
            return
        
        if not self.tracklist:  # if the tracklist is empty
            self.is_playing = False  # clear playing state
            self.is_paused = False  # clear paused state
            self.checking = False  # stop the end checker
            self.tracklist_playing = False  # clear tracklist mode
            self._reset_playback_buttons()  # restore button labels
            self.status_text.set("List is empty. Please add some tracks in.")  # show a message
            return
        
        next_index = self.current_index + self.tracklist_step  # calculate the next index

        if self.tracklist_loop:  # if tracklist looping is enabled
            next_index = self._wrap_tracklist_index(next_index)  # wrap around the list
        elif next_index < 0 or next_index >= len(self.tracklist):  # if the next index is out of range
            self.is_playing = False  # clear playing state
            self.is_paused = False  # clear paused state
            self.checking = False  # stop the end checker
            self.tracklist_playing = False  # clear tracklist mode
            self._reset_playback_buttons()  # restore button labels
            self.status_text.set("Played all tracks in tracklist.")  # show completion
            return
        
        while 0 <= next_index < len(self.tracklist):  # keep trying tracks until one plays or the list ends
            track_number = self.tracklist[next_index]  # get the next track number
            name = self.library.get_name(track_number) or "Unknown"  # get a readable name
            looping = self._is_looped_track(next_index)  # check whether this track should loop

            if self.library.play_track(track_number, loop = looping):  # try to play the track
                self.library.increment_play_count(track_number)  # increase the play count
                self.current_index = next_index  # store the active index
                self.current_track_number = track_number  # store the current track number
                self.current_track_length = self.library.get_track_length(track_number)  # cache the track length
                self.current_track_offset = 0.0  # reset the offset
                self.playback_mode = "tracklist"  # mark playback as tracklist mode
                self.status_text.set(f"Played '{name}'.")  # show a success message

                if not looping:  # only schedule an end check when the track does not loop
                    self.after_id = self.window.after(1000, self._check_track_end(playback_id))  # schedule the next check
                return
            
            self.current_index = next_index  # still update the current index
            self.current_track_number = track_number  # store the failed track number
            self.current_track_length = 0.0  # clear the cached length for the failed track
            self.status_text.set(f"Error playing '{name}', skipping to next track.")  # show an error and skip on

            next_index += self.tracklist_step  # advance to the next item
            
            if self.tracklist_loop:  # if looping is enabled
                next_index = self._wrap_tracklist_index(next_index)  # wrap around the list
            elif next_index < 0 or next_index >= len(self.tracklist):  # stop if the list ends
                break

        self.is_playing = False  # clear playing state
        self.is_paused = False  # clear paused state
        self.checking = False  # stop the end checker
        self.tracklist_playing = False  # clear tracklist mode
        self._reset_playback_buttons()  # restore button labels
        self.status_text.set("Played all tracks in tracklist.")  # show a completion message

                





    # Update the loop button text to reflect the current loop state.
    def toggle_tracklist_loop_ui(self):
        self.tracklist_loop = not self.tracklist_loop  # flip the loop flag
        if self.tracklist_loop:
            self.loop_button.configure(text = "Loop On")  # update the button label
            self.status_text.set("Tracklist loop enabled.")  # confirm the change
        else: 
            self.loop_button.configure(text = "Loop Off")  # update the button label
            self.status_text.set("Tracklist loop is not enabled.")  # confirm the change
    
    # Wrap an index around the tracklist when looping is enabled.
    def _wrap_tracklist_index(self, index):
        if not self.tracklist:  # reject empty lists
            return None
        return index % len(self.tracklist)  # wrap the index within the list bounds
    
    # Restart the currently active looped track from the beginning.
    def _restart_active_track(self):
        if self.playback_mode == "single" and self.current_track_number is not None:  # if a single track is playing
            if self.current_track_number in self.looped_track_numbers:  # if that track is looped
                self.playback_id += 1  # advance the session ID
                self._stop_current_playback()  # stop the current audio
                self.is_playing = True  # mark playback active again
                self.is_paused = False  # clear paused state
                self.checking = True  # re-enable end checking
                self._play_track_number(self.current_track_number)  # restart the current track
                self.status_text.set("Restarted current track.")  # show a confirmation
                return True
            
        if self.playback_mode == "tracklist" and self.current_index < len(self.tracklist):  # if tracklist playback is active
            if self._is_looped_track(self.current_index):  # if the current list entry is looped
                self.playback_id += 1  # advance the session ID
                self._stop_current_playback()  # stop the current audio
                self.is_playing = True  # mark playback active again
                self.is_paused = False  # clear paused state
                self.checking = True  # re-enable end checking
                self._play_track_at_index(self.current_index, self.playback_id)  # restart the current list entry
                self.status_text.set("Restarted current track.")  # show a confirmation
                return True
            
        return False  # nothing was restarted
    

    
    # Check whether a tracklist position or track number is looped.
    def _is_looped_track(self, index):
        if index < 0 or index >= len(self.tracklist):  # reject invalid indexes
            return False
        
        track_number = self.tracklist[index]  # read the track number at the given position
        return index in self.looped_positions or track_number in self.looped_track_numbers  # check both loop sets
    
    # Normalize user-entered track numbers before using them in the library.
    def _normalize_track_number_input(self, raw_track):
        raw_track = raw_track.strip()  # remove extra whitespace
        if not raw_track:  # reject blank input
            return None
        if raw_track.isdigit():  # normalize numeric track numbers
            return raw_track.zfill(2)  # pad to two digits
        return raw_track.upper()  # normalize custom IDs

    




    # Play the track at one specific tracklist index.
    def _play_track_at_index(self, index, playback_id = None):
        self.current_track_offset = 0.0  # reset the seek offset
        if index < 0 or index >= len(self.tracklist):  # reject invalid indexes
            self.status_text.set("Error occurred. Please try again.")  # show an error
            return
        
        if playback_id is None:  # default to the current session if none was provided
            playback_id = self.playback_id

        track_number = self.tracklist[index]  # read the track number from the list
        name = self.library.get_name(track_number) or "Unknown"  # get a readable name
        looping = self._is_looped_track(index)  # check whether this track should loop

        if self.library.play_track(track_number, loop = looping):  # try to play the selected track
            self.library.increment_play_count(track_number)  # increase the play count
            self.status_text.set(f"Played '{name}'.")  # show a success message
        else:
            self.status_text.set(f"Error playing '{name}', please try again.")  # show an error if playback fails
        
        self.current_index = index  # store the current index
        self.current_track_number = track_number  # store the active track number
        self.current_track_length = self.library.get_track_length(track_number)  # cache the track length
        self.current_track_offset = 0.0  # reset the offset
        self.playback_mode = "tracklist"  # mark playback as tracklist mode

        if not looping:  # only schedule an end check when the track does not loop
            self.after_id = self.window.after(1000, lambda: self._check_track_end(playback_id))  # schedule the next check
    

    


    # Move forward one track, or restart the active looped track if needed.
    def skip_track(self):
        if not self.tracklist_playing and self.playback_mode != "single":  # reject when nothing is active
            self.status_text.set("Nothing is currently playing.")  # tell the user nothing is playing
            return
        
        if self._restart_active_track():  # restart a looped track if needed
            return
        
        if self.playback_mode == "single":  # if single-track mode is active
            if self.current_track_number is None:  # reject missing track numbers
                self.status_text.set("Please enter a track number.")  # prompt the user
                return
            
            self.playback_id += 1  # advance the session ID
            self._stop_current_playback()  # stop the current audio
            self.is_playing = True  # mark playback active again
            self.is_paused = False  # clear paused state
            self.checking = True  # re-enable end checking
            self._play_track_number(self.current_track_number)  # restart the same track
            self.status_text.set("Restarted current track.")  # show a message
            return
        
        if not self.tracklist:  # reject empty lists
            self.status_text.set("List is empty. Please add some tracks in.")  # prompt the user
            return
        
        self.tracklist_step = 1  # ensure we are moving forward
        next_index = self.current_index + 1  # calculate the next index

        if self.tracklist_loop:  # if wrapping is enabled
            next_index = self._wrap_tracklist_index(next_index)  # wrap around the list
        elif next_index >= len(self.tracklist):  # if the end is reached
            self.status_text.set("You are the end of the tracklist.")  # show an end-of-list message
            return
        
        self.playback_id += 1  # advance the session ID
        self._stop_current_playback()  # stop the current audio
        self.is_playing = True  # mark playback active again
        self.is_paused = False  # clear paused state
        self.checking = True  # re-enable end checking

        self._play_track_at_index(next_index, self.playback_id)  # play the next track

    # Move backward one track, or restart the active looped track if needed.
    def reverse_track(self):
        if not self.tracklist_playing and self.playback_mode != "single":  # reject when nothing is active
            self.status_text.set("Nothing is currently playing.")  # tell the user nothing is playing
            return
        
        if self._restart_active_track():  # restart a looped track if needed
            return
        
        if self.playback_mode == "single":  # if single-track mode is active
            if self.current_track_number is None:  # reject missing track numbers
                self.status_text.set("Please enter a track number.")  # prompt the user
                return
            
            self.playback_id += 1  # advance the session ID
            self._stop_current_playback()  # stop the current audio
            self.is_playing = True  # mark playback active again
            self.is_paused = False  # clear paused state
            self.checking = True  # re-enable end checking
            self._play_track_number(self.current_track_number)  # restart the same track
            return
        
        if not self.tracklist:  # reject empty lists
            self.status_text.set("List is empty. Please add some tracks in.")  # prompt the user
            return
        
        self.tracklist_step = -1  # ensure we are moving backward
        previous_index = self.current_index - 1  # calculate the previous index

        if self.tracklist_loop:  # if wrapping is enabled
            previous_index = self._wrap_tracklist_index(previous_index)  # wrap around the list
        elif previous_index < 0:  # if the start is reached
            self.status_text.set("You are at the beginning of the tracklist.")  # show a start-of-list message
            return
        
        self.playback_id += 1  # advance the session ID
        self._stop_current_playback()  # stop the current audio
        self.is_playing = True  # mark playback active again
        self.is_paused = False  # clear paused state
        self.checking = True  # re-enable end checking

        self._play_track_at_index(previous_index, self.playback_id)  # play the previous track

            


    # Resume paused tracklist playback.
    def resume_playback(self):
        self._mixer_check()  # ensure pygame is available

        if not self.is_paused:  # only resume if playback is paused
            self.status_text.set("Playback is active.")  # tell the user playback is already active
            return
        
        pygame.mixer.music.unpause()  # resume the audio
        self.is_playing = True  # mark playback active
        self.is_paused = False  # clear paused state
        self.checking = True  # re-enable end checking
        self.status_text.set("Playback resumed.")  # show a confirmation message

        if self.after_id:  # cancel any previous end-check timer
            self.window.after_cancel(self.after_id)  # cancel the scheduled callback
            self.after_id = None  # clear the timer ID

        if self.playback_mode == "tracklist":  # if tracklist playback is active
            self.after_id = self.window.after(1000, lambda: self._check_track_end(self.playback_id))  # restart the end checker


    # Stop playback and reset the playback state.
    def stop_playback(self):
        self.is_playing = False  # clear playing state
        self.is_paused = False  # clear paused state
        self.checking = False  # disable end checking
        self.current_index = 0  # reset the current index
        self.current_track_length = 0.0  # clear the cached track length
        self.playback_mode = None  # clear the playback mode
        self.playback_id += 1  # invalidate older playback timers
        self.tracklist_playing = False  # clear tracklist playback mode

        if self.after_id:  # cancel any end-check timer
            self.window.after_cancel(self.after_id)  # cancel the scheduled callback
            self.after_id = None  # clear the timer ID
        
        if self.progress_after_id:  # cancel any progress update timer
            self.window.after_cancel(self.progress_after_id)  # cancel the scheduled callback
            self.progress_after_id = None  # clear the timer ID

        self._mixer_check()  # ensure pygame is available
        pygame.mixer.music.stop()  # stop the audio
        self.status_text.set("Playback stopped.")  # confirm the stop

        self.progress_value.set(0)  # reset the seek slider
        self.progress_text.set("00:00 / 00:00")  # reset the time label
        self._reset_playback_buttons()  # restore button labels

        self._update_progress_bar()  # refresh the progress display
    
    # Pause the active tracklist playback.
    def pause_playback(self):
        self._mixer_check()  # ensure pygame is available

        if not self.is_playing and not self.is_paused:  # reject if nothing is active
            self.status_text.set("Nothing is currently playing.")  # tell the user nothing is playing
            return
        
        pygame.mixer.music.pause()  # pause the audio
        self.is_playing = False  # clear playing state
        self.is_paused = True  # mark playback paused
        self.checking = False  # disable end checking
        self.status_text.set("Playback paused.")  # confirm the pause

        if self.after_id:  # cancel any end-check timer
            self.window.after_cancel(self.after_id)  # cancel the scheduled callback
            self.after_id = None  # clear the timer ID
    
        
    # Stop the current track and cancel the scheduled end check.
    def _stop_current_playback(self):
        if self.after_id:  # cancel any end-check timer
            self.window.after_cancel(self.after_id)  # cancel the scheduled callback
            self.after_id = None  # clear the timer ID
        
        self._mixer_check()  # ensure pygame is available
        pygame.mixer.music.stop()  # stop the audio

    # Stop a single track directly through pygame.
    def _stop_single_track(self):
        self._mixer_check()  # ensure pygame is available
        pygame.mixer.music.stop()  # stop the audio


    # Detect when the current track ends and queue the next one if needed.
    def _check_track_end(self, playback_id = None):
        if playback_id is None:  # default to the current playback session
            playback_id = self.playback_id
        
        if playback_id != self.playback_id or not self.is_playing:  # ignore stale timers or inactive playback
            return
        
        if self.is_paused:  # if playback is paused
            self.after_id = self.window.after(1000, lambda: self._check_track_end(playback_id))  # check again later
            return
        
        if self.current_track_number is None:  # reject missing track information
            return
        
        if pygame.mixer.music.get_busy():  # if audio is still playing
            self.after_id = self.window.after(1000, lambda: self._check_track_end(playback_id))  # check again later
            return
        
        if self.playback_mode == "tracklist":  # if tracklist playback is active
            self._play_next_in_tracklist(playback_id)  # move to the next track


    # Initialize pygame audio if it has not been started yet.
    def _mixer_check(self):
        if pygame.mixer.get_init() is None:  # if the mixer has not been initialized yet
            pygame.mixer.init()  # initialize pygame audio

    # Clear the tracklist and remove all loop markers.
    def reset_tracklist(self):
        self.tracklist.clear()  # remove all tracks from the list
        self._refresh_tracklist_text()  # redraw the tracklist panel
        self.looped_positions.clear()  # remove all looped positions
        self.looped_track_numbers.clear()  # remove all looped track numbers
        self.status_text.set("Tracklist cleared.")  # confirm the reset

    
    # Play one track directly from the track number input.
    def _play_track_number(self, track_number):
        self.current_track_offset = 0.0  # reset the seek offset
        name = self.library.get_name(track_number)  # look up the track name
        if name is None:  # reject invalid tracks
            self.status_text.set("Please enter a track number.")  # prompt the user
            return
        
        self._mixer_check()  # ensure pygame is available
        pygame.mixer.music.stop()  # stop any existing audio

        if self.library.play_track(track_number):  # try to play the selected track
            self.library.increment_play_count(track_number)  # increase the play count
            self.status_text.set(f"Played '{name}'.")  # show a success message
            self.is_playing = True  # mark playback active
            self.is_paused = False  # clear paused state
            self.checking = True  # enable end-of-track checking
            self.playback_mode = "single"  # mark single-track mode
            self.current_track_number = track_number  # store the active track number
            self.current_track_length = self.library.get_track_length(track_number)  # cache the track length
            self.current_track_offset = 0.0  # reset the offset
            self.current_index = -1  # clear the tracklist index
            self.checking = True  # keep checking enabled
        else:
            self.status_text.set(f"Error playing '{name}'. Please try again.")  # show an error message

    # Read the track number field and play that track.
    def play_track(self):
        raw = self.track_input.get().strip()  # read the input field
        track_number = raw.zfill(2) if raw.isdigit() else raw  # normalize numeric track numbers
        self._play_track_number(track_number)  # play the selected track

    # Shuffle the order of tracks in the current tracklist.
    def shuffle_tracklist(self):
        if len(self.tracklist) < 2:  # require at least two tracks
            self.status_text.set("Need at least 2 tracks to shuffle.")  # tell the user why nothing happened
            return
        random.shuffle(self.tracklist)  # randomize the list order
        self._refresh_tracklist_text()  # redraw the tracklist panel
        self.status_text.set("Tracklist shuffled.")  # confirm the shuffle

    # Remove one track from the current tracklist.
    def remove_track(self):
        raw = self.track_input.get().strip()  # read the input field
        track_number = raw.zfill(2) if raw.isdigit() else raw  # normalize numeric track numbers
        for index, saved_track_number in enumerate(self.tracklist):  # search the current tracklist
            if saved_track_number == track_number:  # if the requested track is found
                del self.tracklist[index]  # remove it from the list
                self._refresh_tracklist_text()  # redraw the list
                removed_name = self.library.get_name(track_number) or "track"  # get a friendly display name
                self.status_text.set(f"Removed '{removed_name}' from tracklist.")  # confirm the removal
                return
        self.status_text.set("Track not found in tracklist.")  # tell the user nothing was removed

    # Play a track by its visible position in the tracklist.
    def play_specific_track(self):
        raw_position = self.tracklist_position.get().strip()  # read the visible position field
        if not raw_position.isdigit():  # reject non-numeric input
            self.status_text.set("Please enter a valid track position.")  # prompt the user
            return
        position = int(raw_position)  # convert the position to an integer
        if position < 1 or position > len(self.tracklist):  # ensure the position is in range
            self.status_text.set("Invalid track position.")  # show an error
            return
        track_number = self.tracklist[position - 1]  # convert from 1-based position to list index
        self._play_track_number(track_number)  # play the selected track

    # Save the current tracklist to CSV.
    def save_tracklist(self):
        try:
            with self.tracklist_file.open("w", newline="", encoding="utf-8") as file:  # open the CSV file for writing
                writer = csv.writer(file)  # create a CSV writer
                writer.writerow(["track_number", "name", "artist", "audio_path"])  # write the header row
                for track_number in self.tracklist:  # save every track in the list
                    item = self.library.library.get(track_number)  # fetch the library item
                    if item is None:  # skip missing items
                        continue
                    audio_path = str(item.audio_path) if item.audio_path else ""  # write the audio path as text
                    writer.writerow([track_number, item.name, item.artist, audio_path])  # write one track entry
            self.status_text.set(f"Tracklist saved to {self.tracklist_file.name}.")  # confirm the save
        except OSError:
            self.status_text.set("Could not save tracklist.")  # show an error if saving fails

    # Load the saved tracklist from CSV and recreate any custom tracks.
    def load_tracklist(self, auto_load = False):
        if not self.tracklist_file.exists():  # reject missing files
            if not auto_load:  # avoid noisy messages during auto-load
                self.status_text.set("No saved tracklist found.")  # tell the user nothing was loaded
            return

        try:
            loaded_tracklist = []  # collect loaded track numbers here
            with self.tracklist_file.open("r", newline="", encoding="utf-8") as file:  # open the CSV file for reading
                reader = csv.DictReader(file)  # read rows by column name
                for row in reader:  # inspect each saved row
                    track_number = row.get("track_number", "").strip()  # read the track number
                    if not track_number:  # skip empty rows
                        continue

                    normalised_number = track_number.zfill(2) if track_number.isdigit() else track_number  # normalize numeric track numbers
                    name = row.get("name", "").strip()  # read the track name
                    artist = row.get("artist", "").strip()  # read the artist name
                    audio_path = row.get("audio_path", "").strip()  # read the audio path

                    if normalised_number not in self.library.library and name and artist:  # recreate missing custom tracks
                        self.library.add_custom_track(normalised_number, name, artist, audio_path)  # add the custom track to the library
                    loaded_tracklist.append(normalised_number)  # add the track number to the loaded list

            self.tracklist = loaded_tracklist  # replace the current tracklist
            self._refresh_tracklist_text()  # redraw the tracklist panel
            if not auto_load:  # only show a message during manual load
                self.status_text.set(f"Tracklist loaded from {self.tracklist_file.name}.")  # confirm the load
        except (OSError, KeyError):
            if not auto_load:  # only show an error during manual load
                self.status_text.set("Could not load saved tracklist.")  # show an error message

    # Generate a new custom track ID that does not collide with existing tracks.
    def _next_custom_track_id(self):
        index = 1  # start custom track numbering at 1
        while True:
            track_id = f"CUST{index:03d}"  # build a custom track ID
            if track_id not in self.library.library:  # if the ID is unused
                return track_id  # return it
            index += 1  # otherwise try the next number
    
    # Reset the playback button labels after stopping.
    def _reset_playback_buttons(self):
        if getattr(self, "play_stop_button", None) is not None:  # if the play/stop button exists
            self.play_stop_button.configure(text = "Play Tracklist")  # restore the default label
        if getattr(self, "pause_resume_button", None) is not None:  # if the pause/resume button exists
            self.pause_resume_button.configure(text = "Pause")  # restore the default label

    # Read the selected tracklist position from the input field.
    def _get_selected_tracklist_index(self):
        raw_position = self.tracklist_position.get().strip()  # read the visible position input
        if not raw_position.isdigit():  # reject non-numeric input
            return None
        
        index = int(raw_position) - 1  # convert from 1-based display index to list index
        if index < 0 or index >= len(self.tracklist):  # reject out-of-range values
            return None
        return index  # return the valid index
    
if __name__ == "__main__":  # allow this file to run directly for testing
    root = tk.Tk()  # create the root window
    font.configure()  # configure the fonts

    theme_mode = Path(__file__).with_name("saved_theme.txt")  # this is a path object in the current code
    if theme_mode == "System":  # check whether system theme is selected
        font.apply_device_theme(root)  # apply the OS theme
    else:
        font.apply_theme(root, theme_mode)  # apply the selected theme

    CreateTracklist(root, theme_mode = theme_mode)  # create the tracklist manager
    root.mainloop()  # start the Tk event loop
