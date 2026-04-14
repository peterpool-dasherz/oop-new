import tkinter as tk
from tkinter import ttk

import font_manager as font
import track_library_oop as lib


class UpdateTracks:
    def __init__(self, window, library=None):
        self.window = window
        self.window.title("Update Track Rating")
        self.window.geometry("760x420")
        self.library = library or lib.TrackLibrary()
        self.track_input = tk.StringVar()
        self.rating_input = tk.StringVar()
        self.status_text = tk.StringVar(value = "Please enter track number and rating to update (tracks are rated from 1 to 5)")

        form = ttk.LabelFrame(window, text = "Update Rating", padding = 12)
        form.pack(fill = "x", padx = 12, pady = (12, 8))

        ttk.Label(form, text = "Track Number").grid(row = 0, column = 0, sticky = "w")
        ttk.Entry(form, width = 10, textvariable = self.track_input).grid(row = 0, column = 1, padx = (6, 18))
        ttk.Label(form, text = "New Rating").grid(row = 0, column = 2, sticky = "w")
        ttk.Entry(form, width = 10, textvariable = self.rating_input).grid(row = 0, column = 3, padx = (6, 18))
        ttk.Button(form, text = "Update Track Rating", command = self.update_track).grid(row = 0, column = 4)

        self.output = tk.Text(window, width = 64, height = 12)
        self.output.pack(fill = "both", expand = True, padx = 12, pady = (0, 6))
        self.set_text(self.output, "")
        status_label = ttk.Label(window, textvariable = self.status_text, padding = (12, 6)).pack(fill = "x")

    def set_text(self, text_area, content):
        text_area.configure(state = "normal")
        text_area.delete("1.0", tk.END)
        text_area.insert("1.0", content)
        text_area.configure(state = "disabled")
    
    def update_track(self):
        raw_track = self.track_input.get().strip()
        raw_rating = self.rating_input.get().strip()

        if not raw_track.isdigit():
            self.status_text.set("Track number invalid, please enter a valid track number.")
            return
        
        if not raw_rating.isdigit() or not (1 <= int(raw_rating) <= 5):
            self.status_text.set("Rating must be between 1 and 5.")
            return

        track_number = raw_track.zfill(2)
        name = self.library.get_name(track_number)
        if not name:
            self.status_text.set("No track with that number is found.")
            return
        
        self.library.set_rating(track_number, int(raw_rating))
        artist = self.library.get_artist(track_number)
        plays = self.library.get_play_count(track_number)

        self.set_text(
            self.output,
            f"Track updated successfully\n\n"
            f"Track: {name}\n"
            f"Artist: {artist}\n"
            f"Plays: {plays}\n"
            f"Rating: {raw_rating}"
        )
        self.status_text.set("Track rating updated successfully")

if __name__ == "__main__":
    root = tk.Tk()
    font.configure()
    UpdateTracks(root)
    root.mainloop()
