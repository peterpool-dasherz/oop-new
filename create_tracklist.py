from struct import pack
import tkinter as tk
from tkinter import ttk
import csv
from pathlib import Path
import random
import font_manager as font
import track_library_oop as lib
import pygame 
from tkinter import messagebox



class CreateTracklist:
    def __init__(self, window, library = None, theme_mode = "System"):
        self.window = window
        self.window.title("Create Tracklist")
        self.window.geometry("1300x850")
        self.library = library or lib.TrackLibrary()
        self.track_input = tk.StringVar()
        self.tracklist_position = tk.StringVar()
        self.tracklist = []
        self.status_text = tk.StringVar(value = "Please insert track number to add tracks to your tracklist")
        self.tracklist_file = Path(__file__).with_name("saved_tracklist.csv")
        self.custom_track_name = tk.StringVar()
        self.custom_track_artist = tk.StringVar()
        self.custom_track_path = tk.StringVar()
        self.current_index = -1
        self.is_playing = False
        self.is_paused = False
        self.after_id = None
        self.playback_id = 0
        self.checking = False
        self.theme_mode = theme_mode
        self.tracklist_step = 1
        self.tracklist_loop = False
        self.tracklist_playing = False
        self.looped_positions = set()
        self.looped_track_numbers = set()

        self.playback_mode = None
        self.current_track_number = None
        self.progress_after_id = None
        self.progress_value = tk.DoubleVar(value = 0)
        self.progress_text = tk.StringVar(value = "00:00 / 00:00")
        self.current_track_length = 0.0
        

        controls = ttk.Frame(window, padding = 10)
        controls.pack(fill = "x")

        main_area = ttk.Frame(window, padding = (10, 0, 10, 0))
        main_area.pack(side = "top", fill = "both", expand = True)

        self.tracklist_text = tk.Text(main_area, height = 18, width = 102, bg = "#31384a", fg = "#e7eaf0", insertbackground = "#e7eaf0", selectbackground = "#5f8fbe")
        self.tracklist_text.pack(fill = "both", expand = True)
        self.set_text(self.tracklist_text, "")
        self.load_tracklist(auto_load = True)

        




        track_frame = ttk.LabelFrame(controls, text = "Track Actions", padding = 8)
        track_frame.grid(row = 0, column = 0, sticky = "ew", padx = 4, pady = 4)
        ttk.Label(track_frame, text = "Track Number").grid(row = 0, column = 0, sticky = "w", padx = (0, 6))
        ttk.Entry(track_frame, width = 8, textvariable = self.track_input).grid(row = 0, column = 1, padx = (0, 10))
        ttk.Button(track_frame, text = "Add Track", command = self.add_track).grid(row = 0, column = 2, padx = 4)
        ttk.Button(track_frame, text = "Play", command = self.play_track).grid(row = 0, column = 3, padx = 4)
        ttk.Button(track_frame, text = "Remove", command = self.remove_track).grid(row = 0, column = 4, padx = 4)

        position_frame = ttk.LabelFrame(controls, text = "Track Position", padding = 8)
        position_frame.grid(row = 0, column = 1, sticky = "ew", padx = 4, pady = 4)
        ttk.Label(position_frame, text = "Position").grid(row = 0, column = 0, sticky = "w", padx = (0, 6))
        ttk.Entry(position_frame, width = 8, textvariable = self.tracklist_position).grid(row = 0, column = 1, padx = (0, 10))
        ttk.Button(position_frame, text = "Play Position", command = self.play_specific_track).grid(row = 0, column = 2, padx = 4)

        
        custom_frame = ttk.LabelFrame(controls, text = "Custom Track", padding = 8)
        custom_frame.grid(row = 2, column = 0, columnspan = 2, sticky = "ew", padx = 4, pady = 4)
        ttk.Label(custom_frame, text = "Name").grid(row = 0, column = 0, sticky = "w", padx = (0, 6))
        ttk.Entry(custom_frame, width = 20, textvariable = self.custom_track_name).grid(row = 0, column = 1, padx = (0, 10))
        ttk.Label(custom_frame, text = "Artist").grid(row = 0, column = 2, sticky = "w", padx = (0, 6))
        ttk.Entry(custom_frame, width = 20, textvariable = self.custom_track_artist).grid(row = 0, column = 3, padx = (0, 10))
        ttk.Label(custom_frame, text = "Path").grid(row = 1, column = 0, sticky = "w", padx = (0, 6), pady = (8, 0))
        ttk.Entry(custom_frame, width = 48, textvariable = self.custom_track_path).grid(row = 1, column = 1, columnspan = 3, sticky = "ew", padx = (0, 10), pady = (8, 0))
        ttk.Button(custom_frame, text = "Add Custom Track", command = self.add_custom_track).grid(row = 1, column = 4, padx = 4, pady = (8, 0))

        library_frame = ttk.LabelFrame(controls, text = "Tracklist Management", padding = 8)
        library_frame.grid(row = 3, column = 0, columnspan = 2, sticky = "ew", padx = 4, pady = 4)
        ttk.Button(library_frame, text = "Shuffle", command = self.shuffle_tracklist).grid(row = 0, column = 0, padx = 4)
        ttk.Button(library_frame, text = "Reset", command = self.reset_tracklist).grid(row = 0, column = 1, padx = 4)
        ttk.Button(library_frame, text = "Save", command = self.save_tracklist).grid(row = 0, column = 2, padx = 4)
        ttk.Button(library_frame, text = "Load", command = self.load_tracklist).grid(row = 0, column = 3, padx = 4)

        bottom_bar = ttk.Frame(window, padding = 10)
        bottom_bar.pack(side = "bottom", fill = "x")

        playback_frame = ttk.LabelFrame(bottom_bar, text = "Playback", padding = 8)
        playback_frame.pack(fill = "x", pady = (0, 6))

        self.play_stop_button = ttk.Button(playback_frame, text = "Play / Stop tracklist", command = self.toggle_play_stop)
        self.play_stop_button.grid(row = 0, column = 0, padx = 4)
        self.pause_resume_button = ttk.Button(playback_frame, text = "Pause / Resume", command = self.toggle_pause_resume)
        self.pause_resume_button.grid(row = 0, column = 1, padx = 4)
        ttk.Button(playback_frame, text = "Skip", command = self.skip_track).grid(row = 0, column = 2, padx = 4)
        ttk.Button(playback_frame, text = "Reverse", command = self.reverse_track).grid(row = 0, column = 3, padx = 4)
        self.loop_button = ttk.Button(playback_frame, text = "Loop Tracklist", command = self.toggle_tracklist_loop_ui)
        self.loop_button.grid(row = 0, column = 4, padx = 4)
        self.loop_track_button = ttk.Button(playback_frame, text = "Loop Selected Track", command = self.toggle_selected_track_loop)
        self.loop_track_button.grid(row = 0, column = 5, padx = 4)
        self.loop_track_number_button = ttk.Button(playback_frame, text = "Loop Track Number", command = self.toggle_selected_track_number_loop)
        self.loop_track_number_button.grid(row = 0, column = 6, padx = 4)

        progress_frame = ttk.Frame(window, padding = (10, 0, 10, 0))
        progress_frame.pack(fill = "x")

        self.progress_bar = ttk.Progressbar(progress_frame, orient = "horizontal", mode = "determinate", maximum = 100, variable = self.progress_value)
        self.progress_bar.pack(fill = "x")
        ttk.Label(progress_frame, textvariable = self.progress_text).pack(anchor = "e")





        ttk.Label(bottom_bar, textvariable = self.status_text, padding = (10, 8)).pack(fill = "x")

        if self.theme_mode == "System":
            font.apply_device_theme(self.window)
        else:
            font.apply_theme(self.window, self.theme_mode)
        
        self._update_progress_bar()
        
    def set_text(self, text_area, content):
        text_area.configure(state = "normal")
        text_area.delete("1.0", tk.END)
        text_area.insert("1.0", content)
        text_area.configure(state = "disabled")

    def _format_tracklist(self):
        lines = []
        for index, track_number in enumerate(self.tracklist):
            name = self.library.get_name(track_number) or "Unknown"
            artist = self.library.get_artist(track_number)
            if artist:
                lines.append(f"{index + 1}. {name} - {artist} ({track_number})")
            else:
                lines.append(f"{index + 1}. {name} ({track_number})")
        return "\n".join(lines)
    
    def _format_time(self, seconds):
        seconds = max(0, int(seconds))
        return f"{seconds // 60:02d}:{seconds % 60:02d}"
    
    def _update_progress_bar(self):
        try:
            if self.current_track_number is None or self.current_track_length <= 0:
                self.progress_value.set(0)
                self.progress_text.set("00:00 / 00:00")
            
            elif self.is_playing or self.is_paused:
                pos_ms = pygame.mixer.music.get_pos()

                if pos_ms < 0:
                    elapsed = 0
                else:
                    elapsed = min(pos_ms / 1000.0, self.current_track_length)
                
                percent = (elapsed / self.current_track_length) * 100
                self.progress_value.set(percent)
                self.progress_text.set(f"{self._format_time(elapsed)} / {self._format_time(self.current_track_length)}")
            
            else:
                self.progress_value.set(0)
                self.progress_text.set("00:00 / 00")
            
        except Exception:
            self.progress_value.set(0)
            self.progress_text.set("00:00 / 00:00")
        
        self.progress_after_id = self.window.after(250, self._update_progress_bar)



    def _refresh_tracklist_text(self):
        self.set_text(self.tracklist_text, self._format_tracklist())

    def add_track(self):
        raw = self.track_input.get().strip()
        track_number = raw.zfill(2) if raw.isdigit() else raw
        
        name = self.library.get_name(track_number)
        if not name:
            self.status_text.set("Invalid track number, please enter a valid track number.")
            return
        
        if track_number in self.tracklist:
            confirm = messagebox.askyesno("Duplicate track", f"'{name}' is already in your tracklist.\n\ Add it anyway?")
            if not confirm:
                self.status_text.set("Track is not added.")
                return
            

        self.tracklist.append(track_number)
        self._refresh_tracklist_text()
        self.status_text.set(f"Added '{name}' to tracklist.")

    def add_custom_track(self):
        custom_name = self.custom_track_name.get().strip()
        custom_artist = self.custom_track_artist.get().strip()
        custom_path = self.custom_track_path.get().strip()

        if not custom_name:
            self.status_text.set("Please enter a custom track name.")
            return

        if not custom_artist:
            self.status_text.set("Please enter a custom artist.")
            return

        if not custom_path:
            self.status_text.set("Please enter the audio file path.")
            return

        if not Path(custom_path).exists():
            self.status_text.set("Audio file not found at that path.")
            return

        custom_track_id = self._next_custom_track_id()
        self.library.add_custom_track(custom_track_id, custom_name, custom_artist, custom_path)
        self.tracklist.append(custom_track_id)
        self._refresh_tracklist_text()
        self.custom_track_name.set("")
        self.custom_track_artist.set("")
        self.custom_track_path.set("")
        self.status_text.set(f"Added custom track '{custom_name}' to tracklist.")

    def play_tracklist(self):
        if not self.tracklist:
            self.status_text.set("List is empty. Please add some tracks in.")
            return
        
        self.stop_playback()
        self.playback_id += 1
        self.current_index = -1
        self.tracklist_step = 1
        self.is_playing = True
        self.is_paused = False
        self.checking = True
        self.tracklist_playing = True

        if getattr(self, "play_stop_button", None) is not None:
            self.play_stop_button.configure(text = "Stop Tracklist")
        if getattr(self, "pause_resume_button", None) is not None:
            self.pause_resume_button.configure(text = "Pause")
        
        self._play_next_in_tracklist(self.playback_id) 


    def toggle_play_stop(self):
        if self.tracklist_playing or self.is_playing or self.is_paused:
            self.stop_playback()
        else:
            self.play_tracklist()
            self.play_stop_button.configure(text = "Stop Tracklist")
            self.pause_resume_button.configure(text = "Pause")
    
    def toggle_pause_resume(self):
        if self.is_paused:
            self.resume_playback()
            self.pause_resume_button.configure(text = "Pause")
        else:
            self.pause_playback()
            self.pause_resume_button.configure(text = "Resume")
    
    def toggle_tracklist_loop(self):
        self.tracklist_loop = not self.tracklist_loop
        return self.tracklist_loop 
    
    def toggle_selected_track_loop(self):
        index = self._get_selected_tracklist_index()
        if index is None:
            self.status_text.set("Please enter the position of the track.")
            return
        
        if index in self.looped_positions:
            self.looped_positions.remove(index)
            self.status_text.set(f"Loop disabled for track {index + 1}.")
        else:
            self.looped_positions.add(index)
            self.status_text.set(f"Loop enabled for track {index + 1}.")
    
    def toggle_selected_track_number_loop(self):
        raw_track = self.track_input.get().strip()
        track_number = self._normalize_track_number_input(raw_track)

        if not track_number:
            self.status_text.set("Please enter a track number.")
            return
        
        if track_number not in self.library.library:
            self.status_text.set("Track not found.")
            return
        
        if track_number in self.looped_track_numbers:
            self.looped_track_numbers.remove(track_number)
            self.status_text.set(f"Loop disabled for track: {track_number}.")
        else:
            self.looped_track_numbers.add(track_number)
            self.status_text.set(f"Loop enabled for track: {track_number}.")
        




    def _play_next_in_tracklist(self, playback_id):
        if playback_id != self.playback_id or not self.is_playing:
            return
        
        if not self.tracklist:
            self.is_playing = False
            self.is_paused = False
            self.checking = False
            self.tracklist_playing = False
            self._reset_playback_buttons()
            self.status_text.set("List is empty. Please add some tracks in.")
            return
        
        next_index = self.current_index + self.tracklist_step

        if self.tracklist_loop:
            next_index = self._wrap_tracklist_index(next_index)
        elif next_index < 0 or next_index >= len(self.tracklist):
            self.is_playing = False
            self.is_paused = False
            self.checking = False
            self.tracklist_playing = False
            self._reset_playback_buttons()
            self.status_text.set("Played all tracks in tracklist.")
            return
        
        while 0 <= next_index < len(self.tracklist):
            track_number = self.tracklist[next_index]
            name = self.library.get_name(track_number) or "Unknown"
            looping = self._is_looped_track(next_index)

            if self.library.play_track(track_number, loop = looping):
                self.library.increment_play_count(track_number)
                self.current_index = next_index
                self.current_track_number = track_number
                self.current_track_length = self.library.get_track_length(track_number)
                self.playback_mode = "tracklist"
                self.status_text.set(f"Played '{name}'.")

                if not looping:
                    self.after_id = self.window.after(1000, self._check_track_end(playback_id))
                return
            
            self.current_index = next_index
            self.current_track_number = track_number 
            self.current_track_length = 0.0
            self.status_text.set(f"Error playing '{name}', skipping to next track.")

            next_index += self.tracklist_step
            
            if self.tracklist_loop:
                next_index = self._wrap_tracklist_index(next_index)
            elif next_index < 0 or next_index >= len(self.tracklist):
                break

        self.is_playing = False
        self.is_paused = False
        self.checking = False
        self.tracklist_playing = False
        self._reset_playback_buttons()
        self.status_text.set("Played all tracks in tracklist.")

                





    def toggle_tracklist_loop_ui(self):
        self.tracklist_loop = not self.tracklist_loop 
        if self.tracklist_loop:
            self.loop_button.configure(text = "Loop On")
            self.status_text.set("Tracklist loop enabled.")
        else: 
            self.loop_button.configure(text = "Loop Off")
            self.status_text.set("Tracklist loop is not enabled.")
    
    def _wrap_tracklist_index(self, index):
        if not self.tracklist:
            return None
        return index % len(self.tracklist)
    
    def _restart_active_track(self):
        if self.playback_mode == "single" and self.current_track_number is not None:
            if self.current_track_number in self.looped_track_numbers:
                self.playback_id += 1
                self._stop_current_playback()
                self.is_playing = True
                self.is_paused = False
                self.checking = True
                self._play_track_number(self.current_track_number)
                self.status_text.set("Restarted current track.")
                return True
            
        if self.playback_mode == "tracklist" and self.current_index < len(self.tracklist):
            if self._is_looped_track(self.current_index):
                self.playback_id += 1
                self._stop_current_playback()
                self.is_playing = True
                self.is_paused = False
                self.checking = True
                self._play_track_at_index(self.current_index, self.playback_id)
                self.status_text.set("Restarted current track.")
                return True
            
        return False
    

    
    def _is_looped_track(self, index):
        if index < 0 or index >= len(self.tracklist):
            return False
        
        track_number = self.tracklist[index]
        return index in self.looped_positions or track_number in self.looped_track_numbers 
    
    def _normalize_track_number_input(self, raw_track):
        raw_track = raw_track.strip()
        if not raw_track:
            return None
        if raw_track.isdigit():
            return raw_track.zfill(2)
        return raw_track.upper()

    




    def _play_track_at_index(self, index, playback_id = None):
        if index < 0 or index >= len(self.tracklist):
            self.status_text.set("Error occurred. Please try again.")
            return
        
        if playback_id is None:
            playback_id = self.playback_id

        track_number = self.tracklist[index]
        name = self.library.get_name(track_number) or "Unknown"
        looping = self._is_looped_track(index)

        if self.library.play_track(track_number, loop = looping):
            self.library.increment_play_count(track_number)
            self.status_text.set(f"Played '{name}'.")
        else:
            self.status_text.set(f"Error playing '{name}', please try again.")
        
        self.current_index = index
        self.current_track_number = track_number
        self.current_track_length = self.library.get_track_length(track_number)
        self.playback_mode = "tracklist"

        if not looping:
            self.after_id = self.window.after(1000, lambda: self._check_track_end(playback_id))
    

    


    def skip_track(self):
        if not self.tracklist_playing and self.playback_mode != "single":
            self.status_text.set("Nothing is currently playing.")
            return
        
        if self._restart_active_track():
            return
        
        if self.playback_mode == "single":
            if self.current_track_number is None:
                self.status_text.set("Please enter a track number.")
                return
            
            self.playback_id += 1
            self._stop_current_playback()
            self.is_playing = True
            self.is_paused = False
            self.checking = True
            self._play_track_number(self.current_track_number)
            self.status_text.set("Restarted current track.")
            return
        
        if not self.tracklist:
            self.status_text.set("List is empty. Please add some tracks in.")
            return
        
        self.tracklist_step = 1
        next_index = self.current_index + 1

        if self.tracklist_loop:
            next_index = self._wrap_tracklist_index(next_index)
        elif next_index >= len(self.tracklist):
            self.status_text.set("You are the end of the tracklist.")
            return
        
        self.playback_id += 1
        self._stop_current_playback()
        self.is_playing = True
        self.is_paused = False
        self.checking = True

        self._play_track_at_index(next_index, self.playback_id)

    def reverse_track(self):
        if not self.tracklist_playing and self.playback_mode != "single":
            self.status_text.set("Nothing is currently playing.")
            return
        
        if self._restart_active_track():
            return
        
        if self.playback_mode == "single":
            if self.current_track_number is None:
                self.status_text.set("Please enter a track number.")
                return
            
            self.playback_id += 1
            self._stop_current_playback()
            self.is_playing = True
            self.is_paused = False
            self.checking = True
            self._play_track_number(self.current_track_number)
            return
        
        if not self.tracklist:
            self.status_text.set("List is empty. Please add some tracks in.")
            return
        
        self.tracklist_step = -1
        previous_index = self.current_index - 1

        if self.tracklist_loop:
            previous_index = self._wrap_tracklist_index(previous_index)
        elif previous_index < 0:
            self.status_text.set("You are at the beginning of the tracklist.")
            return
        
        self.playback_id += 1
        self._stop_current_playback()
        self.is_playing = True
        self.is_paused = False
        self.checking = True

        self._play_track_at_index(previous_index, self.playback_id)

            


    def resume_playback(self):
        self._mixer_check()

        if not self.is_paused:
            self.status_text.set("Playback is active.")
            return
        
        pygame.mixer.music.unpause()
        self.is_playing = True
        self.is_paused = False
        self.checking = True
        self.status_text.set("Playback resumed.")

        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None

        if self.playback_mode == "tracklist":
            self.after_id = self.window.after(1000, lambda: self._check_track_end(self.playback_id))


    def stop_playback(self):
        self.is_playing = False
        self.is_paused = False
        self.checking = False
        self.current_index = 0
        self.current_track_length = 0.0
        self.playback_mode = None
        self.playback_id += 1
        self.tracklist_playing = False

        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None
        
        if self.progress_after_id:
            self.window.after_cancel(self.progress_after_id)
            self.progress_after_id = None

        self._mixer_check()
        pygame.mixer.music.stop()
        self.status_text.set("Playback stopped.")

        self.progress_value.set(0)
        self.progress_text.set("00:00 / 00:00")
        self._reset_playback_buttons()

        self._update_progress_bar()
        
    def _stop_current_playback(self):
        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None
        
        self._mixer_check()
        pygame.mixer.music.stop()

    def _stop_single_track(self):
        self._mixer_check()
        pygame.mixer.music.stop()


    def _check_track_end(self, playback_id = None):
        if playback_id is None:
            playback_id = self.playback_id
        
        if playback_id != self.playback_id or not self.is_playing:
            return
        
        if self.is_paused:
            self.after_id = self.window.after(1000, lambda: self._check_track_end(playback_id))
            return
        
        if self.current_track_number is None:
            return
        
        if pygame.mixer.music.get_busy():
            self.after_id = self.window.after(1000, lambda: self._check_track_end(playback_id))
            return
        
        if self.playback_mode == "tracklist":
            self._play_next_in_tracklist(playback_id)


    def _mixer_check(self):
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()

    def reset_tracklist(self):
        self.tracklist.clear()
        self._refresh_tracklist_text()
        self.looped_positions.clear()
        self.looped_track_numbers.clear()
        self.status_text.set("Tracklist cleared.")

    
    def _play_track_number(self, track_number):
        name = self.library.get_name(track_number)
        if name is None:
            self.status_text.set("Please enter a track number.")
            return
        
        self._mixer_check()
        pygame.mixer.music.stop()

        if self.library.play_track(track_number):
            self.library.increment_play_count(track_number)
            self.status_text.set(f"Played '{name}'.")
            self.is_playing = True
            self.is_paused = False
            self.checking = True
            self.playback_mode = "single"
            self.current_track_number = track_number
            self.current_track_length = self.library.get_track_length(track_number)
            self.current_index = -1
            self.checking = True
        else:
            self.status_text.set(f"Error playing '{name}'. Please try again.")

    def play_track(self):
        raw = self.track_input.get().strip()
        track_number = raw.zfill(2) if raw.isdigit() else raw
        self._play_track_number(track_number)

    def shuffle_tracklist(self):
        if len(self.tracklist) < 2:
            self.status_text.set("Need at least 2 tracks to shuffle.")
            return
        random.shuffle(self.tracklist)
        self._refresh_tracklist_text()
        self.status_text.set("Tracklist shuffled.")

    def remove_track(self):
        raw = self.track_input.get().strip()
        track_number = raw.zfill(2) if raw.isdigit() else raw
        for index, saved_track_number in enumerate(self.tracklist):
            if saved_track_number == track_number:
                del self.tracklist[index]
                self._refresh_tracklist_text()
                removed_name = self.library.get_name(track_number) or "track"
                self.status_text.set(f"Removed '{removed_name}' from tracklist.")
                return
        self.status_text.set("Track not found in tracklist.")

    def play_specific_track(self):
        raw_position = self.tracklist_position.get().strip()
        if not raw_position.isdigit():
            self.status_text.set("Please enter a valid track position.")
            return
        position = int(raw_position)
        if position < 1 or position  > len(self.tracklist):
            self.status_text.set("Invalid track position.")
            return
        track_number = self.tracklist[position - 1]
        self._play_track_number(track_number)

    def save_tracklist(self):
        try:
            with self.tracklist_file.open("w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["track_number", "name", "artist", "audio_path"])
                for track_number in self.tracklist:
                    item = self.library.library.get(track_number)
                    if item is None:
                        continue
                    audio_path = str(item.audio_path) if item.audio_path else ""
                    writer.writerow([track_number, item.name, item.artist, audio_path])
            self.status_text.set(f"Tracklist saved to {self.tracklist_file.name}.")
        except OSError:
            self.status_text.set("Could not save tracklist.")

    def load_tracklist(self, auto_load = False):
        if not self.tracklist_file.exists():
            if not auto_load:
                self.status_text.set("No saved tracklist found.")
            return

        try:
            loaded_tracklist = []
            with self.tracklist_file.open("r", newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    track_number = row.get("track_number", "").strip()
                    if not track_number:
                        continue

                    normalised_number = track_number.zfill(2) if track_number.isdigit() else track_number
                    name = row.get("name", "").strip()
                    artist = row.get("artist", "").strip()
                    audio_path = row.get("audio_path", "").strip()

                    if normalised_number not in self.library.library and name and artist:
                        self.library.add_custom_track(normalised_number, name, artist, audio_path)
                    loaded_tracklist.append(normalised_number)

            self.tracklist = loaded_tracklist
            self._refresh_tracklist_text()
            if not auto_load:
                self.status_text.set(f"Tracklist loaded from {self.tracklist_file.name}.")
        except (OSError, KeyError):
            if not auto_load:
                self.status_text.set("Could not load saved tracklist.")

    def _next_custom_track_id(self):
        index = 1
        while True:
            track_id = f"CUST{index:03d}"
            if track_id not in self.library.library:
                return track_id
            index += 1
    
    def _reset_playback_buttons(self):
        if getattr(self, "play_stop_button", None) is not None:
            self.play_stop_button.configure(text = "Play Tracklist")
        if getattr(self, "pause_resume_button", None) is not None:
            self.pause_resume_button.configure(text = "Pause")

    def _get_selected_tracklist_index(self):
        raw_position = self.tracklist_position.get().strip()
        if not raw_position.isdigit():
            return None
        
        index = int(raw_position) - 1
        if index < 0 or index >= len(self.tracklist):
            return None
        return index
    
if __name__ == "__main__":
    root = tk.Tk()
    font.configure()

    theme_mode = Path(__file__).with_name("saved_theme.txt")
    if theme_mode == "System":
        font.apply_device_theme(root)
    else:
        font.apply_theme(root, theme_mode)

    CreateTracklist(root, theme_mode = theme_mode)
    root.mainloop()
