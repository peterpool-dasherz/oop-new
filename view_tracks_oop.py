import tkinter as tk
from tkinter import ttk
from pathlib import Path
import font_manager as font
import track_library_oop as lib
import pygame


class TrackViewer:
    # Track browser window for listing, searching, viewing, and controlling playback.
    def __init__(self, window, library = None, theme_mode = "System", on_play_track = None, on_add_to_tracklist = None, on_pause_track = None, on_resume_track = None, on_get_playback_state = None, on_toggle_loop_song = None, on_stop_track = None, on_seek_track = None, on_get_current_track_info = None):
        self.window = window  # store the Tk window for this viewer
        self.window.title("View Tracks")  # set the window title shown in the title bar
        self.window.geometry("1150x650")  # set the default window size
        self.library = library or lib.TrackLibrary()  # use the shared library if supplied

        self.track_input = tk.StringVar()  # store the selected track number
        self.search_input = tk.StringVar()  # store the free-text search query
        self.artists_filter_input = tk.StringVar(value = "All artists")  # store the chosen artist filter
        self.status_text = tk.StringVar(value = "Please enter track number to view track")  # store the status message shown at the bottom

        self.theme_mode = theme_mode  # remember the current theme selection
        self.on_play_track = on_play_track  # callback used to play a selected track
        self.on_add_to_tracklist = on_add_to_tracklist  # callback used to add a track to the tracklist
        self.on_pause_track = on_pause_track  # callback used to pause playback
        self.on_resume_track = on_resume_track  # callback used to resume playback
        self.on_stop_track = on_stop_track  # callback used to stop playback
        self.on_get_playback_state = on_get_playback_state  # callback used to read playback state
        self.on_toggle_loop_song = on_toggle_loop_song  # callback used to toggle looping
        self.on_seek_track = on_seek_track  # callback used to seek within the current track
        self.on_get_current_track_info = on_get_current_track_info  # callback used to fetch current track metadata
        self.current_track_number = None  # cache the active track number for the progress slider
        self.current_track_length = 0.0  # cache the active track length for the progress slider
        self.current_track_offset = 0.0  # store the seek offset so displayed time stays correct
        self.progress_after_id = None  # store the Tk timer ID for the progress refresh loop
        self.progress_value = tk.DoubleVar(value = 0)  # store the slider percentage as a numeric Tk variable
        self.progress_text = tk.StringVar(value = "00:00 / 00:00")  # store the time label text

        controls = ttk.Frame(self.window, padding = 10)  # top control bar container
        controls.pack(fill = "x")  # stretch the control bar horizontally

        top_row = ttk.Frame(controls)  # first row of track actions
        top_row.pack(fill = "x", pady = (0, 8))  # add spacing below the row

        ttk.Button(top_row, text = "List All Tracks", command = self.list_tracks).pack(side = "left", padx = (0, 8))  # show all tracks
        ttk.Label(top_row, text = "Track Number").pack(side = "left", padx = (12, 4))  # label the track number field
        ttk.Entry(top_row, width = 8, textvariable = self.track_input).pack(side = "left", padx = (0, 8))  # track number input box
        ttk.Button(top_row, text = "View Track", command = self.view_tracks).pack(side = "left")  # show one track's details
        ttk.Button(top_row, text = "Play selected track", command = self.toggle_play_pause).pack(side = "left", padx = (0, 8))  # start or control playback
        ttk.Button(top_row, text = "Add to Tracklist", command = self.add_selected_to_tracklist).pack(side = "left")  # add selected track to playlist
        ttk.Button(top_row, text = "Loop Song", command = self.toggle_loop_song).pack(side = "left", padx = (0, 8))  # toggle single-track looping
        ttk.Button(top_row, text = "Stop", command = self.stop_playback).pack(side = "left", padx= (0, 8))  # stop playback
    
        

        search_row = ttk.Frame(controls)  # second row for search and filtering
        search_row.pack(fill = "x")  # stretch this row horizontally

        ttk.Label(search_row, text = "Search").pack(side = "left", padx = (0, 4))  # label the search box
        ttk.Entry(search_row, width = 28, textvariable = self.search_input).pack(side = "left", padx = (0, 10))  # search query field
        ttk.Button(search_row, text = "Search", command = self.search_tracks).pack(side = "left", padx = (0, 18))  # run the search

        ttk.Label(search_row, text = "Filter by Artist").pack(side = "left", padx = (0, 4))  # label the artist dropdown
        self.artists_filter_combobox = ttk.Combobox(  # dropdown used to filter tracks by artist
            search_row,
            width = 24,
            textvariable = self.artists_filter_input,
            values = ["All artists", *self.library.list_artists()],
            state = "readonly"
        )
        self.artists_filter_combobox.pack(side = "left", padx = (0, 8))  # place the dropdown in the row
        ttk.Button(search_row, text = "Apply", command = self.filter_tracks).pack(side = "left")  # apply the chosen artist filter

        content = ttk.Frame(self.window, padding = (10, 0, 10, 0))  # main body container
        content.pack(fill = "both", expand = True)  # allow the body to expand with the window

        list_panel = ttk.LabelFrame(content, text = "Track List", padding = 8)  # left panel for the track list
        list_panel.pack(side = "left", fill = "both", expand = True)  # stretch the panel to fill remaining space
        self.list_text = tk.Text(list_panel, height = 22, width = 76, bg = "#31384a", fg = "#e7eaf0", insertbackground = "#e7eaf0", selectbackground = "#5f8fbe")  # text widget for track list output
        self.list_text.pack(fill = "both", expand = True)  # make the list text fill the panel

        detail_panel = ttk.LabelFrame(content, text = "Track Details", padding = 8)  # right panel for one-track details
        detail_panel.pack(side = "left", fill = "y", padx = (12, 0))  # position the panel to the right
        self.detail_text = tk.Text(detail_panel, height = 22, width = 28, bg = "#31384a", fg = "#e7eaf0", insertbackground = "#e7eaf0", selectbackground = "#5f8fbe")  # text widget for details output
        self.detail_text.pack(fill = "both", expand = True)  # make the details fill the panel

        status_bar = ttk.Label(self.window, textvariable = self.status_text, padding = (10, 8))  # status message line at the bottom
        status_bar.pack(fill = "x")  # stretch the status bar across the window
        self.refresh_artist_options()  # populate the artist dropdown with current artists

        progress_frame = ttk.Frame(self.window, padding = (10, 0, 10, 0))  # container for the seek slider
        progress_frame.pack(fill = "x")  # stretch the progress area across the window

        self.progress_bar = tk.Scale(progress_frame, from_ = 0, to = 100, orient = "horizontal", showvalue = False, resolution = 0.1, variable = self.progress_value, length = 500, command = self.seek_change)  # draggable slider for seeking
        self.progress_bar.pack(fill = "x")  # stretch the slider across the window

        self.progress_bar.bind("<ButtonPress-1>", self._begin_seek)  # remember when the user starts dragging
        self.progress_bar.bind("<ButtonRelease-1>", self._end_seek)  # perform the seek when dragging ends

        ttk.Label(progress_frame, textvariable = self.progress_text).pack(anchor = "e")  # show the current time label


        if self.theme_mode == "System":  # apply the system theme if requested
            font.apply_device_theme(self.window)  # use the operating system theme
        else:
            font.apply_theme(self.window, self.theme_mode)  # apply the selected custom theme

        self._update_progress_bar()  # start the repeating progress refresh loop
        

    # Replace the contents of a text widget with new text.
    def set_text(self, text_area, content):
        text_area.configure(state = "normal")
        text_area.delete("1.0", tk.END)
        text_area.insert("1.0", content)
        text_area.configure(state = "disabled")

    # Refresh the artist dropdown from the current library contents.
    def refresh_artist_options(self):
        self.artists_filter_combobox["values"] = ["All artists", *self.library.list_artists()]

    # Show every track in the library.
    def list_tracks(self):
        self.refresh_artist_options()
        self.set_text(self.list_text, self.library.list_all())
        self.artists_filter_input.set("All artists")
        self.status_text.set("List tracks button was clicked (all tracks displayed)")
        self.refresh_artist_options()
    
    # Display the metadata for one selected track number.
    def view_tracks(self):
        raw_track = self.track_input.get().strip()
        if not raw_track:
            self.status_text.set("Please enter a valid track number to view.")
            return
        
        track_number = raw_track
        if track_number.isdigit():
            track_number = track_number.zfill(2)
        else:
            track_number = track_number.upper()
        name = self.library.get_name(track_number)
        if name is None:
            self.status_text.set("No track found with the given track number.")
            return
        artist = self.library.get_artist(track_number)
        rating = self.library.get_rating(track_number)
        play_count = self.library.get_play_count(track_number)

        self.set_text(self.detail_text, f"Track Number: {track_number}\nName: {name}\nArtist: {artist}\nRating: {rating}\nPlay Count: {play_count}")
        self.status_text.set("Track details displayed for track number " + track_number)
    # Search tracks by name or artist text.
    def search_tracks(self):
        query = self.search_input.get().strip()
        selected_artist = self.artists_filter_input.get().strip()
        if not query and selected_artist == "All artists":
            self.status_text.set("Enter search query or select artist.")
            return
        result = self.library.search_and_filter(query, selected_artist)
        if not result:
            self.set_text(self.list_text, "No tracks matched")
            self.status_text.set("Search returned 0 matches")
            return
        self.set_text(self.list_text, result)
        count = len(result.splitlines())
        self.status_text.set(f"{count} tracks matched with request (Search button was clicked)")

    # Filter the track list by the selected artist.
    def filter_tracks(self):
        self.refresh_artist_options()
        selected_artist = self.artists_filter_input.get().strip()
        if selected_artist == "All artists":
            self.list_tracks()
            return
        filter_result = self.library.filter_by_artist(selected_artist)
        if not filter_result:
            self.set_text(self.list_text, "No tracks matched")
            self.status_text.set("Filter returned 0 matches")
            return
        
        self.set_text(self.list_text, filter_result)
        count = len(filter_result.splitlines())
        self.status_text.set(f"{count} tracks matched with request (Filter button was clicked)")
        self.refresh_artist_options()

    # Clear the viewer panels and reset the input fields.
    def clear_all(self):
        self.set_text(self.list_text, "")
        self.set_text(self.detail_text, "")
        self.track_input.set("")
        self.search_input.set("")
        self.artists_filter_input.set("All artists")
        self.current_track_number = None
        self.current_track_length = 0.0
        self.progress_value.set(0)
        self.progress_text.set("00:00 / 00:00")
        self.status_text.set("All fields cleared")
    
    # Normalize the entered track number so it matches the library format.
    def _get_track_number_from_input(self):
        raw_track = self.track_input.get().strip()
        if not raw_track:
            return None
        if raw_track.isdigit():
            return raw_track.zfill(2)
        return raw_track.upper()
    
    # Convert a time value into mm:ss format for the progress label.
    def _format_time(self, seconds):
        seconds = max(0, int(seconds))
        return f"{seconds // 60:02d} : {seconds % 60:02d}"
    
    # Refresh the progress slider and time label from the active track state.
    def _update_progress_bar(self):
        try:
            if self.on_get_current_track_info is not None:
                track_number, total, offset = self.on_get_current_track_info()
                self.current_track_number = track_number 
                self.current_track_length = total
                self.current_track_offset = offset
            
            if self.current_track_number is None or self.current_track_length <= 0:
                self.progress_value.set(0)
                self.progress_text.set("00:00 / 00:00")
            
            elif self.on_get_playback_state is not None:
                is_playing, is_paused = self.on_get_playback_state()

                if is_playing or is_paused:
                    if not self.is_seeking:
                        pos_ms = pygame.mixer.music.get_pos()
                        if pos_ms < 0:
                            elapsed = 0
                        else:
                            elapsed = min(self.current_track_offset + (pos_ms / 1000.0), self.current_track_length)
                        
                        percent = (elapsed / self.current_track_length) * 100
                        self.progress_value.set(percent)
                        self.progress_text.set(f"{self._format_time(elapsed)} / {self._format_time(self.current_track_length)}")
                    
                else:
                    self.progress_value.set(0)
                    self.progress_text.set("00:00 / 00:00")
            
            else:
                self.progress_value.set(0)
                self.progress_text.set("00:00 / 00:00")
        
        except Exception:
            self.progress_value.set(0)
            self.progress_text.set("00:00 / 00:00")
        
        self.progress_after_id = self.window.after(250, self._update_progress_bar)



    # Mark the slider as being dragged so automatic updates do not overwrite it.
    def _begin_seek(self, event = None):
        self.is_seeking = True
    
    # Update the time preview while the slider is being dragged.
    def seek_change(self, value):
        if self.current_track_length <= 0:
            return
        
        try:
            seek_percent = float(value)
        except (TypeError, ValueError):
            return
        
        seek_seconds = (seek_percent / 100.0) * self.current_track_length
        self.progress_text.set(f"{self._format_time(seek_seconds)} / {self._format_time(self.current_track_length)}")
    
    # Seek the current track to the chosen position when the mouse is released.
    def _end_seek(self, event = None):
        if self.on_seek_track is None:
            self.is_seeking = False
            return
        
        if self.current_track_number is None or self.current_track_length <= 0:
            self.is_seeking = False
            return
        
        seek_percent = float(self.progress_value.get())
        seek_seconds = (seek_percent / 100.0)* self.current_track_length

        if self.on_seek_track(seek_seconds):
            self.current_track_offset = self.current_track_offset 
            self.progress_text.set(f"{self._format_time(seek_seconds)} / {self._format_time(self.current_track_length)}")
        else:
            self.status_text.set("Error occurred.")
        
        self.is_seeking = False




    
    
    # Stop playback through the TrackPlayer callback and reset the cached state.
    def stop_playback(self):
        if self.on_stop_track is None:
            self.status_text.set("Error occurred. Please try again.")
            return
        
        if self.on_stop_track():
            self.current_track_number = None
            self.current_track_length = 0.0
            self.current_track_offset = 0.0
            self.progress_value.set(0)
            self.progress_text.set("00:00 / 00:00")
            self.status_text.set("Playback stopped.")
        else:
            self.status_text.set("Error occurred. Please try again.")




    
    
    # Start, pause, or resume playback depending on the current audio state.
    def toggle_play_pause(self):
        track_number = self._get_track_number_from_input()
        if not track_number:
            self.status_text.set("Please enter a track number.")
            return
        
        if self.on_play_track is None or self.on_pause_track is None or self.on_resume_track is None or self.on_get_playback_state is None:
            self.status_text.set("Error occurred. Please try again.")
            return
        
        name = self.library.get_name(track_number) or track_number
        is_playing, is_paused = self.on_get_playback_state()

        if is_paused:
            if self.on_resume_track():
                self.current_track_number = track_number 
                self.current_track_length = self.library.get_track_length(track_number)
                self.status_text.set("Playback resumed.")
            else:
                self.status_text.set("Error occurred.")
            return
        
        if is_playing:
            if self.on_pause_track():
                self.status_text.set("Playback paused.")
            else:
                self.status_text.set("Error occurred.")
            return
        
        if self.on_play_track(track_number):
            self.current_track_number = track_number 
            self.current_track_length = self.library.get_track_length(track_number)
            self.current_track_offset = 0.0
            self.progress_value.set(0)
            self.progress_text.set(f"00:00 / {self._format_time(self.current_track_length)}")
            self.status_text.set(f"Played '{name}'.")
        else:
            self.status_text.set("Error occurred. Please try again.")

            







    # Toggle looping for the currently selected single track.
    def toggle_loop_song(self):
        if self.on_toggle_loop_song is None:
            self.status_text.set("Error occurred. Please try again.")
            return
        
        looping = self.on_toggle_loop_song()
        if looping:
            self.status_text.set("Song loop enabled.")
        else:
            self.status_text.set("Song loop disabled.")
        

    # Add the selected track to the shared tracklist.
    def add_selected_to_tracklist(self):
        track_number = self._get_track_number_from_input()
        if not track_number:
            self.status_text.set("Please enter a track number.")
            return
        
        if self.on_add_to_tracklist is None:
            self.status_text.set("Error occurred, please try again.")
            return
        
        if self.on_add_to_tracklist(track_number):
            self.status_text.set(f"Added '{track_number}' to tracklist.")
        else:
            self.status_text.set("Error occurred, please try again.")

if __name__ == "__main__":
    main_window = tk.Tk()
    font.configure()
    theme_mode = font.load_theme_mode(Path(__file__).with_name("saved_theme.txt"))
    if theme_mode == "System":
        font.apply_device_theme(main_window)
    else:
        font.apply_theme(main_window, theme_mode)
    TrackViewer(main_window, theme_mode = theme_mode)
    main_window.mainloop()
