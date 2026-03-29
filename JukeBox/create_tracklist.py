import tkinter as tk
from tkinter import ttk

import font_manager as font
import track_library_oop as lib

def set_text(text_area, content):
    text_area.configure(state = "normal")
    text_area.delete("1.0", tk.END)
    text_area.insert("1.0", content)
    text_area.config(state = "disabled")

class CreateTracklist:
    def __init__(self, window):
        self.window = window
        self.window.title("Create Tracklist")
        self.geometry = "900x500"
        self.track_input = tk.StringVar()
        self.tracklist = []
        self.status_text = tk.StringVar(value = "Please insert track number to add tracks to your tracklist")
        
        controls = ttk.Frame(window, padding = 10)
        controls.pack(fill = "x")
        track_number_label = ttk.Label(controls, text = "Track Number").pack(side = "left")
        track_number_entry = ttk.Entry(controls, width = 8, textvariable = self.track_input).pack(side = "left", padx = 8)
        add_track_button = ttk.Button(controls, text = "Add Track", command = self.add_track).pack(side = "left", padx = 8)
        play_tracklist_button = ttk.Button(controls, text = "Play Tracklist", command = self.play_tracklist).pack(side = "left", padx = 8)
        reset_tracklist_button = ttk.Button(controls, text = "Reset Tracklist", command = self.reset_tracklist).pack(side = "left", padx = 8)

        self.tracklist_text = tk.Text(window, height = 18, width = 90)
        self.tracklist_text.pack(fill = "both", expand = True, padx = 10, pady = (0, 5))
        set_text(self.tracklist_text, "")
        ttk.Label(window, textvariable = self.status_text, padding = (10, 8)).pack(fill = "x")

    def _format_tracklist(self):
        lines = [f"{index + 1}. {name}" for index, (_, name) in enumerate(self.tracklist)]
        return "\n".join(lines)

    def add_track(self):
        raw = self.track_input.get().strip()
        track_number = raw.zfill(2) if raw.isdigit() else raw
        name = lib.get_name(track_number)
        if not name:
            self.status_text.set("Invalid track number, please enter a valid track number.")
            return
        self.tracklist.append((track_number, name))
        set_text(self.tracklist_text, self._format_tracklist())
        self.status_text.set(f"Added '{name}' to tracklist.")

    def play_tracklist(self):
        if not self.tracklist:
            self.status_text.set("List is empty. Please add some tracks in.")
            return
        for track_number, _ in self.tracklist:
            lib.increment_play_count(track_number)
        self.status_text.set("Played all tracks in tracklist.")

    def reset_tracklist(self):
        self.tracklist.clear()
        set_text(self.tracklist_text, "")
        self.status_text.set("Tracklist reset.")

if __name__ == "__main__":
    root = tk.Tk()
    font.configure()
    CreateTracklist(root)
    root.mainloop()
            
        