import tkinter as tk
from tkinter import ttk
import track_library_oop as lib
import font_manager as font
from create_tracklist import CreateTracklist
from update_tracks import UpdateTracks
from view_tracks_oop import TrackViewer

class TrackPlayer:
    def __init__(self, window):
        self.window = window
        self.window.title("JukeBox")
        self.window.geometry("520x150")
        self.window.configure(bg = "gray")

        self.library = lib.TrackLibrary()

        container = ttk.Frame(window, padding = 10)
        container.pack(fill = "both", expand = True)

        track_player_label = ttk.Label(container, text = "Select an option by clicking one of the buttons below").pack(fill = "x", pady = (0, 20))
        button_row = ttk.Frame(container)
        button_row.pack()

        view_tracks_button = ttk.Button(button_row, text = "Manage Tracks", command = self.open_view_tracks_oop).pack(side = "left", padx = 10)
        create_tracklist_button = ttk.Button(button_row, text = "Manage Tracklist", command = self.open_create_tracklist).pack(side = "left", padx = 10)
        update_tracks_button = ttk.Button(button_row, text = "Update Track Rating", command = self.open_update_tracks).pack(side = "left", padx = 10)
        
    def open_view_tracks_oop(self):
        TrackViewer(tk.Toplevel(self.window), self.library)
    def open_create_tracklist(self):
        CreateTracklist(tk.Toplevel(self.window), self.library)
    def open_update_tracks(self):
        UpdateTracks(tk.Toplevel(self.window), self.library)

if __name__ == "__main__":
    root = tk.Tk()
    font.configure()
    TrackPlayer(root)
    root.mainloop()
