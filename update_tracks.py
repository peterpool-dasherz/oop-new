import tkinter as tk
from tkinter import ttk
from pathlib import Path
import font_manager as font
import track_library_oop as lib


class UpdateTracks:
    def __init__(self, window, library = None, theme_mode = "System"):
        self.window = window
        self.window.title("Update Track Rating")
        self.window.geometry("760x420")
        self.library = library or lib.TrackLibrary()
        self.track_input = tk.StringVar()
        self.rating_input = tk.StringVar()
        self.status_text = tk.StringVar(value = "Please enter track number and rating to update (tracks are rated from 1 to 5)")
        
        self.theme_mode = theme_mode

        form = ttk.LabelFrame(window, text = "Update Rating", padding = 12)
        form.pack(fill = "x", padx = 12, pady = (12, 8))

        ttk.Label(form, text = "Track Number").grid(row = 0, column = 0, sticky = "w")
        ttk.Entry(form, width = 10, textvariable = self.track_input).grid(row = 0, column = 1, padx = (6, 18))
        ttk.Label(form, text = "New Rating").grid(row = 0, column = 2, sticky = "w")
        ttk.Entry(form, width = 10, textvariable = self.rating_input).grid(row = 0, column = 3, padx = (6, 18))
        ttk.Button(form, text = "Update Track Rating", command = self.update_track).grid(row = 0, column = 4)

        self.output = tk.Text(window, width = 64, height = 12, bg = "#31384a", fg = "#e7eaf0", insertbackground = "#e7eaf0", selectbackground = "#5f8fbe")
        self.output.pack(fill = "both", expand = True, padx = 12, pady = (0, 6))
        self.set_text(self.output, "")
        status_label = ttk.Label(window, textvariable = self.status_text, padding = (12, 6)).pack(fill = "x")

        if self.theme_mode == "System":
            font.apply_device_theme(self.window)
        else:
            font.apply_theme(self.window, self.theme_mode)

    def set_text(self, text_area, content):
        text_area.configure(state = "normal")
        text_area.delete("1.0", tk.END)
        text_area.insert("1.0", content)
        text_area.configure(state = "disabled")
    
    def update_track(self):
        raw_track = self.track_input.get().strip()
        raw_rating = self.rating_input.get().strip()
        if not raw_rating.isdigit() or not (1 <= int(raw_rating) <= 5):
            self.status_text.set("Invalid rating. Please enter a number from 1 to 5.")
            return
        track_number = raw_track.strip()
        if track_number.isdigit():
            track_number = track_number.zfill(2)
        else:
            track_number = track_number.upper()
        
        name = self.library.get_name(track_number)
        if name is None:
            self.status_text.set("No track found with the given track number.")
            return
        
        self.library.set_rating(track_number, int(raw_rating))
        artist = self.library.get_artist(track_number)
        plays = self.library.get_play_count(track_number)

        self.set_text(
            self.output,
            f"Updated rating for track {track_number}:\n\nName: {name}\nArtist: {artist}\nRating: {raw_rating}\nPlay Count: {plays}"
        )
        self.status_text.set(f"Successfully updated rating for track {track_number} to {raw_rating}.")
            

if __name__ == "__main__":
    root = tk.Tk()
    font.configure()

    theme_mode = font.load_theme_mode(Path(__file__).with_name("saved_theme.txt"))

    if theme_mode == "System":
        font.apply_device_theme(root)
    else:
        font.apply_theme(root, theme_mode)
    UpdateTracks(root, theme_mode = theme_mode)
    root.mainloop()
