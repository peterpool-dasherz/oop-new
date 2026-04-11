import tkinter as tk
from tkinter import ttk
import csv
from pathlib import Path
import random
import font_manager as font
import track_library_oop as lib


class CreateTracklist:
    def __init__(self, window, library=None):
        self.window = window
        self.window.title("Create Tracklist")
        self.window.geometry("1100x560")
        self.library = library or lib.TrackLibrary()
        self.track_input = tk.StringVar()
        self.tracklist_position = tk.StringVar()
        self.tracklist = []
        self.status_text = tk.StringVar(value = "Please insert track number to add tracks to your tracklist")
        self.tracklist_file = Path(__file__).with_name("saved_tracklist.csv")
        self.custom_track_name = tk.StringVar()
        self.custom_track_artist = tk.StringVar()
        self.custom_track_path = tk.StringVar()

        controls = ttk.Frame(window, padding = 10)
        controls.pack(fill = "x")
        track_number_label = ttk.Label(controls, text = "Track Number")
        track_number_label.grid(row = 0, column = 0, sticky = "w", padx = (0, 5), pady = 4)
        track_number_entry = ttk.Entry(controls, width = 8, textvariable = self.track_input)
        track_number_entry.grid(row = 0, column = 1, padx = (0, 10), pady = 4)
        add_track_button = ttk.Button(controls, text = "Add Track", command = self.add_track)
        add_track_button.grid(row = 0, column = 2, padx = 5, pady = 4)
        play_track_button = ttk.Button(controls, text = "Play by Track Number", command = self.play_track)
        play_track_button.grid(row = 0, column = 3, padx = 5, pady = 4)
        remove_track_button = ttk.Button(controls, text = "Remove Track", command = self.remove_track)
        remove_track_button.grid(row = 0, column = 4, padx = 5, pady = 4)

        tracklist_position_label = ttk.Label(controls, text = "Track Position")
        tracklist_position_label.grid(row = 1, column = 0, sticky = "w", padx = (0, 5), pady = 4)
        tracklist_position_entry = ttk.Entry(controls, width = 8, textvariable = self.tracklist_position)
        tracklist_position_entry.grid(row = 1, column = 1, padx = (0, 10), pady = 4)
        tracklist_position_button = ttk.Button(controls, text = "Play by Track Position", command = self.play_specific_track)
        tracklist_position_button.grid(row = 1, column = 2, padx = 5, pady = 4)
        play_tracklist_button = ttk.Button(controls, text = "Play Tracklist", command = self.play_tracklist)
        play_tracklist_button.grid(row = 1, column = 3, padx = 5, pady = 4)
        shuffle_tracklist_button = ttk.Button(controls, text = "Shuffle Play", command = self.shuffle_tracklist)
        shuffle_tracklist_button.grid(row = 1, column = 4, padx = 5, pady = 4)
        reset_tracklist_button = ttk.Button(controls, text = "Reset Tracklist", command = self.reset_tracklist)
        reset_tracklist_button.grid(row = 1, column = 5, padx = 5, pady = 4)

        save_tracklist_button = ttk.Button(controls, text = "Save Tracklist", command = self.save_tracklist)
        save_tracklist_button.grid(row = 2, column = 2, padx = 5, pady = 4)
        load_tracklist_button = ttk.Button(controls, text = "Load Tracklist", command = self.load_tracklist)
        load_tracklist_button.grid(row = 2, column = 3, padx = 5, pady = 4)

        custom_track_label = ttk.Label(controls, text = "Custom Track")
        custom_track_label.grid(row = 3, column = 0, sticky = "w", padx = (0, 5), pady = 4)
        custom_artist_label = ttk.Label(controls, text = "Custom Artist")
        custom_artist_label.grid(row = 4, column = 0, sticky = "w", padx = (0, 5), pady = 4)
        custom_track_entry = ttk.Entry(controls, width = 24, textvariable = self.custom_track_name)
        custom_track_entry.grid(row = 3, column = 1, columnspan = 2, sticky = "w", padx = (0, 10), pady = 4)
        custom_artist_entry = ttk.Entry(controls, width = 24, textvariable = self.custom_track_artist)
        custom_artist_entry.grid(row = 4, column = 1, columnspan = 2, sticky = "w", padx = (0, 10), pady = 4)

        custom_path_label = ttk.Label(controls, text = "Custom Path")
        custom_path_label.grid(row = 5, column = 0, sticky = "w", padx = (0, 5), pady = 4)
        custom_path_entry = ttk.Entry(controls, width = 24, textvariable = self.custom_track_path)
        custom_path_entry.grid(row = 5, column = 1, columnspan = 2, sticky = "w", padx = (0, 10), pady = 4)

        custom_track_button = ttk.Button(controls, text = "Add Custom Track", command = self.add_custom_track)
        custom_track_button.grid(row = 3, column = 3, padx = 5, pady = 4)

        stop_music_button = ttk.Button(controls, text = "Stop playing", command = self.library.stop_track)
        stop_music_button.grid(row = 3, column = 4, padx = 5, pady = 4)


        self.tracklist_text = tk.Text(window, height = 18, width = 90)
        self.tracklist_text.pack(fill = "both", expand = True, padx = 10, pady = (0, 5))
        self.set_text(self.tracklist_text, "")
        ttk.Label(window, textvariable = self.status_text, padding = (10, 8)).pack(fill = "x")
        self.load_tracklist(auto_load = True)

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
            return
        for track_number in self.tracklist:
            self.library.increment_play_count(track_number)
        self.status_text.set("Played all tracks in tracklist.")

    def reset_tracklist(self):
        self.tracklist.clear()
        self._refresh_tracklist_text()
        self.status_text.set("Tracklist reset.")
    
    def play_track(self):
        raw = self.track_input.get().strip()
        track_number = raw.zfill(2) if raw.isdigit() else raw

        name = self.library.get_name(track_number)
        if not name:
            self.status_text.set("Track not found in the library.")
            return

        if self.library.play_track(track_number):
            self.library.increment_play_count(track_number)
            self.status_text.set(f"Played '{name}'.")
        else:
            self.status_text.set("Error playing track.")

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
        name = self.library.get_name(track_number) or "Unknown"
        if self.library.play_track(track_number):
            self.library.increment_play_count(track_number)
            self.status_text.set(f"Played '{name}'.")
        else:
            self.status_text.set("Error playing track.")

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
    CreateTracklist(root)
    root.mainloop()
