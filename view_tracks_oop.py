import tkinter as tk
from tkinter import ttk

import font_manager as font
import track_library_oop as lib


class TrackViewer:
    def __init__(self, window):
        self.window = window
        self.window.title("View Tracks")
        self.window.geometry("900x500")
        self.library = lib.TrackLibrary()

        self.track_input = tk.StringVar()
        self.search_input = tk.StringVar()
        self.artists_filter_input = tk.StringVar(value = "All artists")
        self.status_text = tk.StringVar(value = "Please enter track number to view track")

        controls = ttk.Frame(self.window, padding = 10)
        controls.pack(fill = "x")

        list_tracks_button = ttk.Button(controls, text = "List All Tracks", command = self.list_tracks).grid(row = 0, column = 0, padx = 5, pady = 4)
        track_number_label = ttk.Label(controls, text = "Enter Track Number").grid(row = 0, column = 2, pady = 4)
        track_number_entry = ttk.Entry(controls, width = 6, textvariable = self.track_input).grid(row = 0, column = 3, padx = 5, pady = 4)
        view_tracks_button = ttk.Button(controls, text = "View Track", command = self.view_tracks).grid(row = 0, column = 4, padx = 10, pady = 4)

        search_label = ttk.Label(controls, text = "Search").grid(row = 0, column = 1, padx = 5, pady = 4)
        search_entry = ttk.Entry(controls, width = 24, textvariable = self.search_input).grid(row = 1, column = 1, columnspan = 2, sticky = "w", pady = 4)
        search_button = ttk.Button(controls, text = "Search", command = self.search_tracks).grid(row = 1, column = 3, padx = 10, pady = 4)

        filter_by_artist_label = ttk.Label(controls, text = "Filter by Artist").grid(row = 1, column = 4, padx = (20, 5), pady = 4)
        self.artists_filter_combobox = ttk.Combobox(controls, width = 22, textvariable = self.artists_filter_input, values = ["All artists", *self.library.list_artists()], state = "readonly").grid(row = 1, column = 5, pady = 4)
        filter_button = ttk.Button(controls, text = "Apply", command = self.filter_tracks).grid(row = 1, column = 6, padx = 10, pady = 4)

        content = ttk.Frame(self.window, padding = (10, 0, 10, 0))
        content.pack(fill = "both", expand = True)

        self.list_text = tk.Text(content, height = 16, width = 60)
        self.list_text.pack(side = "left", fill = "both", expand = True)

        self.detail_text = tk.Text(content, height = 16, width = 30)
        self.detail_text.pack(side = "left", fill = "y", padx = (20, 0))

        status_bar = ttk.Label(self.window, textvariable = self.status_text, padding = (10, 8))
        status_bar.pack(fill = "x")

    def set_text(self, text_area, content):
        text_area.configure(state = "normal")
        text_area.delete("1.0", tk.END)
        text_area.insert("1.0", content)
        text_area.configure(state = "disabled")

    def list_tracks(self):
        self.set_text(self.list_text, self.library.list_all())
        self.artists_filter_input.set("All artists")
        self.status_text.set("List tracks button was clicked (all tracks displayed)")
    
    def view_tracks(self):
        raw_track = self.track_input.get().strip()
        track_number = raw_track.zfill(2)

        name = self.library.get_name(track_number)
        if not name:
            self.set_text(self.detail_text, f"Track {track_number} not found")
            self.status_text.set("Failed to view track because track number is invalid, please input a valid track number")
            return
        
        artist = self.library.get_artist(track_number)
        rating = self.library.get_rating(track_number)
        plays = self.library.get_play_count(track_number)
        track_details = f"{name}\n{artist}\n{rating}\n{plays}"
        self.set_text(self.detail_text, track_details)
        self.status_text.set("Track details displayed successfully (View Track button was clicked)")

    def search_tracks(self):
        query = self.search_input.get().strip()
        result = self.library.search_tracks(query)

        if not query:
            self.status_text.set("Enter artist name to search")
            return
        
        if not result:
            self.set_text(self.list_text, "No tracks matched")
            self.status_text.set("0 tracks matched with request")
            return
        
        self.set_text(self.list_text, result)
        count = len(result.splitlines())
        self.status_text.set(f"{count} tracks matched with request (Search button was clicked)")

    def filter_tracks(self):
        selected_artist = self.artists_filter_input.get().strip()
        if selected_artist == "All artists":
            self.list_tracks()
            return
        filter_result = self.library.filter_by_artist(selected_artist)
        if not filter_result:
            self.set_text(self.list_text, "No tracks matched")
            self.status_text.set("Filter returned 0 matches")
            return
        
        self.set_text(self.list_text, filter_result)
        count = len(filter_result.splitlines())
        self.status_text.set(f"{count} tracks matched with request (Filter button was clicked)")

    def clear_all(self):
        self.set_text(self.list_text, "")
        self.set_text(self.detail_text, "")
        self.track_input.set("")
        self.search_input.set("")
        self.artists_filter_input.set("All artists")
        self.status_text.set("All fields cleared")

if __name__ == "__main__":
    main_window = tk.Tk()
    font.configure()
    TrackViewer(main_window)
    main_window.mainloop()
