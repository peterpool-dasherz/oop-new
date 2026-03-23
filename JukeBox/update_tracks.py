import tkinter as tk
from tkinter import ttk

import font_manager as font
import track_library_oop as lib

def set_text(text_area, content):
    text_area.configure(state = "normal")
    text_area.delete("1.0", tk.END)
    text_area.insert("1.0", content)
    text_area.configure(state = "disabled")

class UpdateTracks:
    def __init__(self, window):
        self.window = window
        self.window.title("Update Tracks")
        self.window.geometry("900x500")
        self.track_input = tk.StringVar()
        self.rating_input = tk.StringVar()
        self.status_text = tk.StringVar(value = "Please enter track number and rating to update (tracks are rated from 1 to 5)")

        form = ttk.Frame(window, padding = 12)
        form.pack(fill = "x")

        track_number_label = ttk.Label(form, text = "Track Number").grid(row = 0, column = 0, sticky = "w")
        track_number_entry = ttk.Entry(form, width = 10, textvariable = self.track_input).grid(row = 0, column = 1, padx = (5, 20))
        rating_label = ttk.Label(form, text = "New Rating").grid(row = 0, column = 2, sticky = "w")
        rating_entry = ttk.Entry(form, width = 10, textvariable = self.rating_input).grid(row = 0, column = 3, padx = 5)
        track_number_button = ttk.Button(form, text = "Update Track", command = self.update_track).grid(row = 0, column = 4, padx = (15, 0))

        self.output = tk.Text(window, width = 70, height = 10)
        self.output.pack(fill = "both", expand = True, padx = 12, pady = (8, 6))
        set_text(self.output, "")
        status_label = ttk.Label(window, textvariable = self.status_text, padding = (12, 6)).pack(fill = "x")
    
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
        name = lib.get_name(track_number)
        if not name:
            self.status_text.set("No track with that number is found.")
            return
        
        lib.set_rating(track_number, int(raw_rating))
        artist = lib.get_artist(track_number)
        plays = lib.get_play_count(track_number)

        set_text(
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