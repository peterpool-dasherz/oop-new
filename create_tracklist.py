from struct import pack
import tkinter as tk
from tkinter import ttk
import csv
from pathlib import Path
import random
import font_manager as font
import track_library_oop as lib
import pygame 



class CreateTracklist:
    def __init__(self, window, library=None):
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
        self.current_index = 0
        self.is_playing = False
        self.is_paused = False
        self.after_id = None
        self.playback_id = 0
        self.checking = False
        

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

        ttk.Label(bottom_bar, textvariable = self.status_text, padding = (10, 8)).pack(fill = "x")

        
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

    def _refresh_tracklist_text(self):
        self.set_text(self.tracklist_text, self._format_tracklist())

    def add_track(self):
        raw = self.track_input.get().strip()
        track_number = raw.zfill(2) if raw.isdigit() else raw
        name = self.library.get_name(track_number)
        if not name:
            self.status_text.set("Invalid track number, please enter a valid track number.")
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
        
        self.stop_playback()
        self.playback_id += 1
        self.current_index = 0
        self.is_playing = True
        self.is_paused = False
        self.checking = True 
        self.play_stop_button.configure(text = "Stop Tracklist")
        self.pause_resume_button.configure(text = "Pause")
        self._play_next_in_tracklist(self.playback_id)


    def toggle_play_stop(self):
        if self.is_playing or self.is_paused:
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
        


    def _play_next_in_tracklist(self, playback_id):
        if playback_id != self.playback_id or not self.is_playing:
            return

        if self.current_index >= len(self.tracklist):
            self.is_playing = False
            self.checking = False
            self.status_text.set("Played all tracks in tracklist.")
            return

        track_number = self.tracklist[self.current_index]
        name = self.library.get_name(track_number) or "Unknown"

        if self.library.play_track(track_number):
            self.library.increment_play_count(track_number)
            self.status_text.set(f"Now playing: '{name}'.")
        else:
            self.status_text.set(f"Error playing '{name}', skipping to next.")

        self.current_index += 1
        self.after_id = self.window.after(1000, lambda: self._check_track_end(playback_id))

    def _play_track_at_index(self, index, playback_id = None):
        if index < 0 or index >= len(self.tracklist):
            self.status_text.set("Error playing track, please try again.")
            return
        
        if playback_id is None:
            playback_id = self.playback_id
        
        self.current_index = index
        track_number = self.tracklist[index]
        name = self.library.get_name(track_number) or "Unknown"

        if self.library.play_track(track_number):
            self.library.increment_play_count(track_number)
            self.status_text.set(f"Now playing: '{name}'.")
        else:
            self.status_text.set(f"Error playing '{name}', skipping to next track.")
        
        self.after_id = self.window.after(1000, lambda: self._check_track_end(playback_id))


    def skip_track(self):
        if not self.tracklist:
            self.status_text.set("List is empty. Please add some tracks in.")
            return
        
        if self.current_index >= len(self.tracklist) - 1:
            self.status_text.set("You've already at the end of the tracklist.")
            return
        
        self.playback_id += 1
        if self.after_id == 1:
            self.window.after_cancel(self.after_id)
            self.after_id = None
        
        self._mixer_check()
        pygame.mixer.music.stop()
        
        self.is_playing = True
        self.is_paused = False
        self.checking = True 

        self._play_track_at_index(self.current_index + 1, self.playback_id)

    def reverse_track(self):
        if not self.tracklist:
            self.status_text.set("List is empty. Please add some tracks in.")
            return
        
        if self.current_index <= 0:
            self.status_text.set("You are at the beginning of the tracklist.")
            return
        
        self.playback_id += 1
        
        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None
        
        self._mixer_check()
        pygame.mixer.music.stop()

        self.is_playing = True
        self.is_paused = False 
        self.checking = True

        self._play_track_at_index(self.current_index - 1, self.playback_id)


    def pause_playback(self):
        self._mixer_check()

        if not self.is_playing and not self.is_paused:
            self.status_text.set("Nothing is currently playing.")
            return
        
        pygame.mixer.music.pause()
        self.is_paused = True
        self.is_playing = False
        self.status_text.set("Playback paused.")




    def resume_playback(self):
        self._mixer_check()

        if not self.is_paused:
            self.status_text.set("Playback is currently active")
            return
        
        pygame.mixer.music.unpause()
        self.is_playing = True
        self.is_paused = False
        self.status_text.set("Playback resumed.")
        self.after_id = self.window.after(1000, self._check_track_end)

    def stop_playback(self):
        self.is_playing = False
        self.is_paused = False
        self.checking = False
        self.current_index = 0
        self.playback_id += 1

        if self.after_id:
            self.window.after_cancel(self.after_id)
            self.after_id = None 
        
        self._mixer_check()
        pygame.mixer.music.stop()
        self.status_text.set("Playback stopped.")

        if hasattr(self, "play_stop_button"):
            self.play_stop_button.configure(text = "Play Tracklist")
        if hasattr(self, "pause_resume_button"):
            self.pause_resume_button.configure(text = "Pause")
        
        if getattr(self, "play_stop_button", None) is not None:
            self.play_stop_button.configure(text = "Play Tracklist")
        if getattr(self, "pause_resume_button", None) is not None:
            self.pause_resume_button.configure(text = "Pause")
    
    def _stop_single_track(self):
        self._mixer_check()
        pygame.music.mixer.stop()


    def _check_track_end(self, playback_id = None):
        if playback_id is None:
            playback_id = self.playback_id
        if playback_id != self.playback_id or not self.is_playing:
            return
        if self.is_paused:
            self.after_id = self.window.after(1000, lambda: self._check_track_end(playback_id))
            return
        if pygame.mixer.music.get_busy():
            self.after_id = self.window.after(1000, lambda: self._check_track_end(playback_id))
            return
        
        self._play_next_in_tracklist(playback_id)

    def _mixer_check(self):
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()

    def reset_tracklist(self):
        self.tracklist.clear()
        self._refresh_tracklist_text()
        self.status_text.set("Tracklist reset.")
    
    def _play_track_number(self, track_number):
        name = self.library.get_name(track_number)
        if name is None:
            self.status_text.set("Track not found.")
            return
        
        self._mixer_check()
        pygame.mixer.music.stop()

        if self.library.play_track(track_number):
            self.library.increment_play_count(track_number)
            self.is_playing = True
            self.is_paused = False
            self.status_text.set(f"Played '{name}'.")
        else:
            self.status_text.set("Error playing track, please try again.")
    
    
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

if __name__ == "__main__":
    root = tk.Tk()
    font.configure()

    theme_mode = Path(__file__).with_name("saved_theme.txt")
    if theme_mode == "System":
        font.apply_device_theme(root)
    else:
        font.apply_theme(root, theme_mode)

    CreateTracklist(root)
    root.mainloop()
