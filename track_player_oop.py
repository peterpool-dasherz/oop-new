import tkinter as tk
from tkinter import ttk
import track_library_oop as lib
import font_manager as font
from create_tracklist import CreateTracklist
from update_tracks import UpdateTracks
from view_tracks_oop import TrackViewer
from pathlib import Path
from tkinter import messagebox

session_file = Path(__file__).with_name("session.txt")

def save_session():
    session_file.write_text("logged in", encoding = "utf-8")

def clear_session():
    if session_file.exists():
        session_file.unlink()

def session_exists():
    return session_file.exists()

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

        self.settings_file = Path(__file__).with_name("saved_theme.txt")
        self.theme_mode = font.load_theme_mode(self.settings_file)
        font.set_theme_mode(self.theme_mode)

        self.is_playing = False
        self.is_paused = False 

        if self.theme_mode == "System":
            font.apply_device_theme(self.window)
        else:
            font.apply_theme(self.window, self.theme_mode)

        self.logout_callback = None
        self.create_tracklist_app = None
        
        self.song_loop = False 

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

        theme_frame = ttk.LabelFrame(container, text = "Theme", padding = 8)
        theme_frame.pack(fill = "x", pady = (16, 0))

        ttk.Label(theme_frame, text = "Select theme:").pack(side = "left", padx = (0, 12))
        ttk.Button(theme_frame, text = "Mirror system settings", command = lambda: self.set_theme("System")).pack(side = "left", padx = 4)
        ttk.Button(theme_frame, text = "Light", command = lambda: self.set_theme("Light")).pack(side = "left", padx = 4)
        ttk.Button(theme_frame, text = "Dark", command = lambda: self.set_theme("Dark")).pack(side = "left", padx = 4)

        ttk.Button(button_row, text = "Logout", command = self.logout).pack(side = "left", padx = 12)

        

    def set_logout_callback(self, callback):
        self.logout_callback = callback
        
    def logout(self):
        clear_session()
        self.library.save_lib_state(self.state_file)
        self.window.destroy()
        if self.logout_callback:
            self.logout_callback()
    
    def open_view_tracks_oop(self):
        TrackViewer(tk.Toplevel(self.window), self.library, theme_mode = self.theme_mode, on_play_track = self.play_track_now, on_add_to_tracklist = self.add_track_to_tracklist, on_pause_track = self.pause_track_now, on_resume_track = self.resume_track_now, on_get_playback_state = self.get_playback_state, on_toggle_loop_song = self.toggle_loop_song)
    def open_create_tracklist(self):
        self.create_tracklist_app = CreateTracklist(tk.Toplevel(self.window), self.library, theme_mode = self.theme_mode)
    def open_update_tracks(self):
        UpdateTracks(tk.Toplevel(self.window), self.library, theme_mode = self.theme_mode)
    def on_close(self):
        self.library.save_lib_state(self.state_file)
        font.save_theme_mode(self.settings_file, self.theme_mode)
        self.window.destroy()
    def set_theme(self, mode):
        self.theme_mode = mode
        font.set_theme_mode(mode)
        font.save_theme_mode(self.settings_file, mode)
        

        if mode == "System":
            font.apply_device_theme(self.window)
        else:
            font.apply_theme(self.window, mode)
    
    def get_playback_state(self):
        return self.is_playing, self.is_paused
    
    def play_track_now(self, track_number):
        if not track_number:
            return False
        
        if track_number.isdigit():
            track_number = track_number.zfill(2)
        else:
            track_number = track_number.upper()
        
        if self.library.get_name(track_number) is None:
            return False
        
        played = self.library.play_track(track_number, loop = self.song_loop)
        if played:
            self.library.increment_play_count(track_number)
            self.tracklist_playing = False
            self.is_playing = True
            self.is_paused = False
        return played
    

    
    def pause_track_now(self):
        if not self.is_playing:
            return False
        
        if self.library.pause_track():
            self.is_playing = False
            self.is_paused = True
            return True
        return False
    

    def resume_track_now(self):
        if not self.is_paused:
            return False
        
        if self.library.resume_track():
            self.is_playing = True
            self.is_pause = False
            return True
        return False
    
    def toggle_song_loop(self):
        self.song_loop = not self.song_loop
        return self.song_loop
    
    

    
    def add_track_to_tracklist(self, track_number):
        if not track_number:
            return False
        
        if track_number.isdigit():
            track_number = track_number.zfill(2)
        else:
            track_number = track_number.upper()
        
        if self.library.get_name(track_number) is None:
            return False
        
        if getattr(self, "create_tracklist_app", None) is None:
            self.open_create_tracklist()
        
        if track_number in self.create_tracklist_app.tracklist:
            track_name = self.library.get_name(track_number) or track_number 
            confirm = messagebox.askyesno("Duplicate track", f"{track_name} is already in your tracklist.\n\ Add it anyway?")
            if not confirm:
                return False
            
        
        self.create_tracklist_app.tracklist.append(track_number)
        self.create_tracklist_app._refresh_tracklist_text()
        self.create_tracklist_app.save_tracklist()
        return True
    
        
        

        
   

class LoginWindow:
    def __init__(self, root, on_success):
        self.root = root
        self.on_success = on_success

        self.root.title = ("Login")
        self.root.geometry = ("360 x 220")
        self.root.resizable(False, False)
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        self.message_var = tk.StringVar(value = "Please login to continue.")

        frame = ttk.Frame(root, padding = 16)
        frame.pack(fill = "both", expand = True)
        ttk.Label(frame, text = "Username").grid(row = 0, column = 0, sticky = "w", pady = (0, 8))
        ttk.Entry(frame, textvariable = self.username_var, width = 28).grid(row = 0, column = 1, pady = (0, 8))

        ttk.Label(frame, text = "Password").grid(row = 1, column = 0, sticky = "w", pady = (0, 8))
        ttk.Entry(frame, textvariable = self.password_var, width = 28, show = "*").grid(row = 1, column = 1, pady = (0, 8))

        ttk.Button(frame, text = "Login", command = self.login).grid(row = 2, column = 0, columnspan = 2, pady = (10, 8))
        ttk.Label(frame, textvariable = self.message_var).grid(row = 3, column = 0, columnspan = 2)
        self.root.bind("<Return>", lambda event: self.login())
    
    def login(self):
        username = self.username_var.get().strip().lower()
        password = self.password_var.get().strip()

        if not username or not password:
            self.message_var.set("Please enter your username and password.")
            return
        if username == "testing account" and password == "123":
            save_session()
            self.root.destroy()
            self.on_success()
        else:
            self.message_var.set("Invalid username or password, please try again.")
    
settings_file = Path(__file__).with_name("saved_theme.txt")
def apply_saved_theme(window):
    theme_mode = font.load_theme_mode(settings_file)
    if theme_mode == "System":
        font.apply_device_theme(window)
    else:
        font.apply_theme(window, theme_mode)

def launch_main_app():
    root = tk.Tk()
    font.configure()
    theme_mode = font.load_theme_mode(Path(__file__).with_name("saved_theme.txt"))
    font.set_theme_mode(theme_mode)

    if theme_mode == "System":
        font.apply_device_theme(root)
    else:
        font.apply_theme(root, theme_mode)
    
    app = TrackPlayer(root)
    app.set_logout_callback(launch_login)
    root.protocol("WM_DELETE_WINDOW", app.on_close)
    root.mainloop()



def launch_login():
    login_root = tk.Tk()
    font.configure()

    theme_mode = font.load_theme_mode(Path(__file__).with_name("saved_theme.txt"))
    font.set_theme_mode(theme_mode)

    if theme_mode == "System":
        font.apply_device_theme(login_root)
    else:
        font.apply_theme(login_root, theme_mode)
    
    LoginWindow(login_root, launch_main_app)
    login_root.mainloop()




if __name__ == "__main__":
    if session_exists():
        launch_main_app()
    else:
        launch_login()