import tkinter as tk
from tkinter import ttk
import random
import font_manager as font
import track_library_oop as lib


class CreateTracklist:
    def __init__(self, window):
        self.window = window
        self.window.title("Create Tracklist")
        self.window.geometry("1100x500")
        self.library = lib.TrackLibrary()
        self.track_input = tk.StringVar()
        self.tracklist_position = tk.StringVar()
        self.tracklist = []
        self.status_text = tk.StringVar(value = "Please insert track number to add tracks to your tracklist")

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


        self.tracklist_text = tk.Text(window, height = 18, width = 90)
        self.tracklist_text.pack(fill = "both", expand = True, padx = 10, pady = (0, 5))
        self.set_text(self.tracklist_text, "")
        ttk.Label(window, textvariable = self.status_text, padding = (10, 8)).pack(fill = "x")

    def set_text(self, text_area, content):
        text_area.configure(state = "normal")
        text_area.delete("1.0", tk.END)
        text_area.insert("1.0", content)
        text_area.configure(state = "disabled")

    def _format_tracklist(self):
        lines = [f"{index + 1}. {name} ({track_number})" for index, (track_number, name) in enumerate(self.tracklist)]
        return "\n".join(lines)

    def add_track(self):
        raw = self.track_input.get().strip()
        track_number = raw.zfill(2) if raw.isdigit() else raw
        name = self.library.get_name(track_number)
        if not name:
            self.status_text.set("Invalid track number, please enter a valid track number.")
            return
        self.tracklist.append((track_number, name))
        self.set_text(self.tracklist_text, self._format_tracklist())
        self.status_text.set(f"Added '{name}' to tracklist.")

    def play_tracklist(self):
        if not self.tracklist:
            self.status_text.set("List is empty. Please add some tracks in.")
            return
        for track_number, _ in self.tracklist:
            self.library.increment_play_count(track_number)
        self.status_text.set("Played all tracks in tracklist.")

    def reset_tracklist(self):
        self.tracklist.clear()
        self.set_text(self.tracklist_text, "")
        self.status_text.set("Tracklist reset.")
    
    def play_track(self):
        raw = self.track_input.get().strip()
        track_number = raw.zfill(2) if raw.isdigit() else raw

        name = self.library.get_name(track_number)
        if not name:
            self.status_text.set("Track not found in the library.")
            return

        self.library.increment_play_count(track_number)
        self.status_text.set(f"Played '{name}'.")

    def shuffle_tracklist(self):
        if len(self.tracklist) < 2:
            self.status_text.set("Need at least 2 tracks to shuffle.")
            return
        random.shuffle(self.tracklist)
        self.set_text(self.tracklist_text, self._format_tracklist())
        self.status_text.set("Tracklist shuffled.")

    def remove_track(self):
        raw = self.track_input.get().strip()
        track_number = raw.zfill(2) if raw.isdigit() else raw
        for index, (saved_track_number, name) in enumerate(self.tracklist):
            if saved_track_number == track_number:
                del self.tracklist[index]
                self.set_text(self.tracklist_text, self._format_tracklist())
                self.status_text.set(f"Removed '{name}' from tracklist.")
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
        track_number, name = self.tracklist[position - 1]
        self.library.increment_play_count(track_number)
        self.status_text.set(f"Played '{name}'.")

if __name__ == "__main__":
    root = tk.Tk()
    font.configure()
    CreateTracklist(root)
    root.mainloop()
