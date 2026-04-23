import tkinter as tk
from tkinter import ttk
from pathlib import Path
import font_manager as font
import track_library_oop as lib
import pygame


class TrackViewer:
    def __init__(self, window, library = None, theme_mode = "System", on_play_track = None, on_add_to_tracklist = None, on_pause_track = None, on_resume_track = None, on_get_playback_state = None, on_toggle_loop_song = None):
        self.window = window
        self.window.title("View Tracks")
        self.window.geometry("1150x650")
        self.library = library or lib.TrackLibrary()

        self.track_input = tk.StringVar()
        self.search_input = tk.StringVar()
        self.artists_filter_input = tk.StringVar(value = "All artists")
        self.status_text = tk.StringVar(value = "Please enter track number to view track")

        self.theme_mode = theme_mode
        self.on_play_track = on_play_track
        self.on_add_to_tracklist = on_add_to_tracklist
        self.on_pause_track = on_pause_track
        self.on_resume_track = on_resume_track
        self.on_get_playback_state = on_get_playback_state
        self.on_toggle_loop_song = on_toggle_loop_song
        self.current_track_number = None
        self.progress_after_id = None
        self.progress_value = None
        self.progress_text = tk.StringVar(value = "00:00 / 00:00")

        controls = ttk.Frame(self.window, padding = 10)
        controls.pack(fill = "x")

        top_row = ttk.Frame(controls)
        top_row.pack(fill = "x", pady = (0, 8))

        ttk.Button(top_row, text = "List All Tracks", command = self.list_tracks).pack(side = "left", padx = (0, 8))
        ttk.Label(top_row, text = "Track Number").pack(side = "left", padx = (12, 4))
        ttk.Entry(top_row, width = 8, textvariable = self.track_input).pack(side = "left", padx = (0, 8))
        ttk.Button(top_row, text = "View Track", command = self.view_tracks).pack(side = "left")
        ttk.Button(top_row, text = "Play selected track", command = self.toggle_play_pause).pack(side = "left", padx = (0, 8))
        ttk.Button(top_row, text = "Add to Tracklist", command = self.add_selected_to_tracklist).pack(side = "left")
        ttk.Button(top_row, text = "Loop Song", command = self.toggle_loop_song).pack(side = "left", padx = (0, 8))

        

        search_row = ttk.Frame(controls)
        search_row.pack(fill = "x")

        ttk.Label(search_row, text = "Search").pack(side = "left", padx = (0, 4))
        ttk.Entry(search_row, width = 28, textvariable = self.search_input).pack(side = "left", padx = (0, 10))
        ttk.Button(search_row, text = "Search", command = self.search_tracks).pack(side = "left", padx = (0, 18))

        ttk.Label(search_row, text = "Filter by Artist").pack(side = "left", padx = (0, 4))
        self.artists_filter_combobox = ttk.Combobox(
            search_row,
            width = 24,
            textvariable = self.artists_filter_input,
            values = ["All artists", *self.library.list_artists()],
            state = "readonly"
        )
        self.artists_filter_combobox.pack(side = "left", padx = (0, 8))
        ttk.Button(search_row, text = "Apply", command = self.filter_tracks).pack(side = "left")

        content = ttk.Frame(self.window, padding = (10, 0, 10, 0))
        content.pack(fill = "both", expand = True)

        list_panel = ttk.LabelFrame(content, text = "Track List", padding = 8)
        list_panel.pack(side = "left", fill = "both", expand = True)
        self.list_text = tk.Text(list_panel, height = 22, width = 76, bg = "#31384a", fg = "#e7eaf0", insertbackground = "#e7eaf0", selectbackground = "#5f8fbe")
            
        self.list_text.pack(fill = "both", expand = True)

        detail_panel = ttk.LabelFrame(content, text = "Track Details", padding = 8)
        detail_panel.pack(side = "left", fill = "y", padx = (12, 0))
        self.detail_text = tk.Text(detail_panel, height = 22, width = 28, bg = "#31384a", fg = "#e7eaf0", insertbackground = "#e7eaf0", selectbackground = "#5f8fbe")
            
        self.detail_text.pack(fill = "both", expand = True)

        status_bar = ttk.Label(self.window, textvariable = self.status_text, padding = (10, 8))
        status_bar.pack(fill = "x")
        self.refresh_artist_options()

        progress_frame = ttk.Frame(self.window, padding = (10, 0, 10, 0))
        progress_frame.pack(fill = "x")

        self.progress_bar = ttk.Progressbar(progress_frame, orient = "horizontal", mode = "determinate", maximum = 100, variable = self.progress_value)
        ttk.Label(progress_frame, textvariable = self.progress_text).pack(anchor = "e")


        if self.theme_mode == "System":
            font.apply_device_theme(self.window)
        else:
            font.apply_theme(self.window, self.theme_mode)

        self._update_progress_bar()
        

    def set_text(self, text_area, content):
        text_area.configure(state = "normal")
        text_area.delete("1.0", tk.END)
        text_area.insert("1.0", content)
        text_area.configure(state = "disabled")

    def refresh_artist_options(self):
        self.artists_filter_combobox["values"] = ["All artists", *self.library.list_artists()]

    def list_tracks(self):
        self.refresh_artist_options()
        self.set_text(self.list_text, self.library.list_all())
        self.artists_filter_input.set("All artists")
        self.status_text.set("List tracks button was clicked (all tracks displayed)")
        self.refresh_artist_options()
    
    def view_tracks(self):
        raw_track = self.track_input.get().strip()
        if not raw_track:
            self.status_text.set("Please enter a valid track number to view.")
            return
        
        track_number = raw_track
        if track_number.isdigit():
            track_number = track_number.zfill(2)
        else:
            track_number = track_number.upper()
        name = self.library.get_name(track_number)
        if name is None:
            self.status_text.set("No track found with the given track number.")
            return
        artist = self.library.get_artist(track_number)
        rating = self.library.get_rating(track_number)
        play_count = self.library.get_play_count(track_number)

        self.set_text(self.detail_text, f"Track Number: {track_number}\nName: {name}\nArtist: {artist}\nRating: {rating}\nPlay Count: {play_count}")
        self.status_text.set("Track details displayed for track number " + track_number)
    def search_tracks(self):
        query = self.search_input.get().strip()
        selected_artist = self.artists_filter_input.get().strip()
        if not query and selected_artist == "All artists":
            self.status_text.set("Enter search query or select artist.")
            return
        result = self.library.search_and_filter(query, selected_artist)
        if not result:
            self.set_text(self.list_text, "No tracks matched")
            self.status_text.set("Search returned 0 matches")
            return
        self.set_text(self.list_text, result)
        count = len(result.splitlines())
        self.status_text.set(f"{count} tracks matched with request (Search button was clicked)")

    def filter_tracks(self):
        self.refresh_artist_options()
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
        self.refresh_artist_options()

    def clear_all(self):
        self.set_text(self.list_text, "")
        self.set_text(self.detail_text, "")
        self.track_input.set("")
        self.search_input.set("")
        self.artists_filter_input.set("All artists")
        self.status_text.set("All fields cleared")
    
    def _get_track_number_from_input(self):
        raw_track = self.track_input.get().strip()
        if not raw_track:
            return None
        if raw_track.isdigit():
            return raw_track.zfill(2)
        return raw_track.upper()
    
    def _format_time(self, seconds):
        seconds = max(0, int(seconds))
        return f"{seconds // 60:02d} : {seconds % 60:02d}"
    
    def _update_progress_bar(self):
        if self.current_track_number is None or self.on_get_playback_state is None:
            self.progress_value.set(0)
            self.progress_text.set("00:00 / 00:00")
            self.progress_after_id = self.window.after(200, self._update_progress_bar)
            return
        
        is_playing, is_paused = self.on_get_playback_state
        total = self.library.get_track_length(self.current_track_number)

        if not is_playing or is_paused:
            self.progress_value.set(0)
            self.progress_text.set("00:00 / 00:00")
            self.progress_after_id = self.window.after(200, self._update_progress_bar)
            return
        
        if total <= 0:
            self.progress_value.set(0)
            self.progress_text.set("00:00 / 00:00")
            self.progress_after_id = self.window.after(200, self._update_progress_bar)

        pos_ms = pygame.mixer.music.get_pos()
        if pos_ms < 0:
            elapsed = 0
        else:
            elapsed = min(pos_ms / 1000.0, total)
        percent = (elapsed / total ) * 100

        self.progress_value.set(percent)
        self.progress_text.set(f"{self._format_time(elapsed)} / {self._format_time(total)}")
        self.progress_after_id = self.window.after(200, self._update_progress_bar)


    
    
    def toggle_play_pause(self):
        track_number = self._get_track_number_from_input()
        if not track_number:
            self.status_text.set("Please enter a track number.")
            return
        
        if self.on_play_track is None or self.on_pause_track is None or self.on_resume_track is None or self.on_get_playback_state is None:
            self.status_text.set("Error occurred. Please try again.")
            return
        
        is_playing, is_paused = self.on_get_playback_state()
        if is_paused:
            if self.on_resume_track():
                name = self.library.get_name(track_number) or track_number 
                self.status_text.set(f"Playback resumed for {name}.")
            else:
                self.status_text.set("Error occurred. Please try again.")
            return
        
        if is_playing:
            if self.on_pause_track():
                name = self.library.get_name(track_number) or track_number 
                self.status_text.set(f"Playback paused for {name}.")
            else:
                self.status_text.set("Error occurred. Please try again.")
            return
        
        if self.on_play_track(track_number):
            name = self.library.get_name(track_number) or track_number
            self.status_text.set(f"Played '{name}'.")
        else:
            self.status_text.set("Error occurred. Please try again.")

    def toggle_loop_song(self):
        if self.on_toggle_loop_song is None:
            self.status_text.set("Error occurred. Please try again.")
            return
        
        looping = self.on_toggle_loop_song()
        if looping:
            self.status_text.set("Song loop enabled.")
        else:
            self.status_text.set("Song loop disabled.")
        

    def add_selected_to_tracklist(self):
        track_number = self._get_track_number_from_input()
        if not track_number:
            self.status_text.set("Please enter a track number.")
            return
        
        if self.on_add_to_tracklist is None:
            self.status_text.set("Error occurred, please try again.")
            return
        
        if self.on_add_to_tracklist(track_number):
            self.status_text.set(f"Added '{track_number}' to tracklist.")
        else:
            self.status_text.set("Error occurred, please try again.")

if __name__ == "__main__":
    main_window = tk.Tk()
    font.configure()
    theme_mode = font.load_theme_mode(Path(__file__).with_name("saved_theme.txt"))
    if theme_mode == "System":
        font.apply_device_theme(main_window)
    else:
        font.apply_theme(main_window, theme_mode)
    TrackViewer(main_window, theme_mode = theme_mode)
    main_window.mainloop()
