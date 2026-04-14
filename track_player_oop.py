import tkinter as tk
from tkinter import ttk
import track_library_oop as lib
import font_manager as font
from create_tracklist import CreateTracklist
from update_tracks import UpdateTracks
from view_tracks_oop import TrackViewer
from pathlib import Path

class TrackPlayer:
    def __init__(self, window):
        self.window = window
        self.window.title("JukeBox")
        self.window.geometry("780x220")
        self.window.configure(bg = "gray")

        self.library = lib.TrackLibrary()
        self.library.load_custom_tracks_from_csv(Path(__file__).with_name("saved_tracklist.csv"))
        self.library.load_lib_state(Path(__file__).with_name("saved_library.csv"))
        self.state_file = Path(__file__).with_name("saved_library.csv")
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        container = ttk.Frame(window, padding = 16)
        container.pack(fill = "both", expand = True)

        track_player_label = ttk.Label(container, text = "Select an option from the buttons below")
        track_player_label.pack(fill = "x", pady = (0, 16))

        button_row = ttk.Frame(container)
        button_row.pack()

        view_tracks_button = ttk.Button(button_row, text = "Manage Tracks", command = self.open_view_tracks_oop)
        view_tracks_button.pack(side = "left", padx = 12)
        create_tracklist_button = ttk.Button(button_row, text = "Manage Tracklist", command = self.open_create_tracklist)
        create_tracklist_button.pack(side = "left", padx = 12)
        update_tracks_button = ttk.Button(button_row, text = "Update Track Rating", command = self.open_update_tracks)
        update_tracks_button.pack(side = "left", padx = 12)
        
    def open_view_tracks_oop(self):
        TrackViewer(tk.Toplevel(self.window), self.library)
    def open_create_tracklist(self):
        CreateTracklist(tk.Toplevel(self.window), self.library)
    def open_update_tracks(self):
        UpdateTracks(tk.Toplevel(self.window), self.library)
    def on_close(self):
        self.library.save_lib_state(self.state_file)
        self.window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    font.configure()
    font.apply_dark_theme(root)
    app = TrackPlayer(root)
    root.protocol( "WM_DELETE_WINDOW", app.on_close)
    root.mainloop()
