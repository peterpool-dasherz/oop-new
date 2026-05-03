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
    # Main application window that opens the viewer, tracklist manager, and rating editor.
    def __init__(self, window):
        self.window = window  # store the main Tk window
        self.window.title("JukeBox")  # set the application title
        self.window.geometry("780x220")  # set the default launcher size
        self.window.configure(bg = "gray")  # apply a simple background color

        self.library = lib.TrackLibrary()  # create the shared track library
        self.library.load_custom_tracks_from_csv(Path(__file__).with_name("saved_tracklist.csv"))  # restore custom tracks
        self.library.load_lib_state(Path(__file__).with_name("saved_library.csv"))  # restore saved ratings and play counts
        self.state_file = Path(__file__).with_name("saved_library.csv")  # remember the library state file path
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)  # save state before closing the app

        self.settings_file = Path(__file__).with_name("saved_theme.txt")  # theme settings file path
        self.theme_mode = font.load_theme_mode(self.settings_file)  # load the saved theme mode
        font.set_theme_mode(self.theme_mode)  # apply the saved theme mode globally

        self.is_playing = False  # track whether a song is currently playing
        self.is_paused = False  # track whether a song is currently paused

        self.song_loop = False  # remember whether single-track looping is enabled

        self.current_track_number = None  # cache the active track number
        self.current_track_length = 0.0  # cache the active track length for seeking
        self.current_track_offset = 0.0  # store the current seek offset

        if self.theme_mode == "System":
            font.apply_device_theme(self.window)
        else:
            font.apply_theme(self.window, self.theme_mode)

        self.logout_callback = None  # callback to run after logout
        self.create_tracklist_app = None  # reference to the tracklist window if it opens
        
        self.song_loop = False  # duplicate initialization kept for current code structure

        container = ttk.Frame(window, padding = 16)  # main launcher container
        container.pack(fill = "both", expand = True)  # stretch the container to fill the window

        track_player_label = ttk.Label(container, text = "Select an option from the buttons below")  # title text
        track_player_label.pack(fill = "x", pady = (0, 16))  # place the title at the top of the window

        button_row = ttk.Frame(container)  # row that holds the main navigation buttons
        button_row.pack()  # place the button row in the launcher

        view_tracks_button = ttk.Button(button_row, text = "Manage Tracks", command = self.open_view_tracks_oop)  # open the track viewer
        view_tracks_button.pack(side = "left", padx = 12)  # place the viewer button
        create_tracklist_button = ttk.Button(button_row, text = "Manage Tracklist", command = self.open_create_tracklist)  # open the tracklist manager
        create_tracklist_button.pack(side = "left", padx = 12)  # place the tracklist button
        update_tracks_button = ttk.Button(button_row, text = "Update Track Rating", command = self.open_update_tracks)  # open the rating editor
        update_tracks_button.pack(side = "left", padx = 12)  # place the update button

        theme_frame = ttk.LabelFrame(container, text = "Theme", padding = 8)  # theme selection section
        theme_frame.pack(fill = "x", pady = (16, 0))  # place the theme controls below the buttons

        ttk.Label(theme_frame, text = "Select theme:").pack(side = "left", padx = (0, 12))  # label for the theme buttons
        ttk.Button(theme_frame, text = "Mirror system settings", command = lambda: self.set_theme("System")).pack(side = "left", padx = 4)  # use the OS theme
        ttk.Button(theme_frame, text = "Light", command = lambda: self.set_theme("Light")).pack(side = "left", padx = 4)  # switch to light mode
        ttk.Button(theme_frame, text = "Dark", command = lambda: self.set_theme("Dark")).pack(side = "left", padx = 4)  # switch to dark mode

        ttk.Button(button_row, text = "Logout", command = self.logout).pack(side = "left", padx = 12)  # let the user log out

        

    # Store the function that should run after logout.
    # Store the callback that should run after logout.
    def set_logout_callback(self, callback):
        self.logout_callback = callback
        
    # Clear the session and close the current application window.
    # Clear the session, save state, and close the launcher window.
    def logout(self):
        clear_session()
        self.library.save_lib_state(self.state_file)
        self.window.destroy()
        if self.logout_callback:
            self.logout_callback()
    
    # Open the track viewer window and pass playback callbacks into it.
    # Open the track viewer and pass the playback callbacks into it.
    def open_view_tracks_oop(self):
        TrackViewer(tk.Toplevel(self.window), self.library, theme_mode = self.theme_mode, on_play_track = self.play_track_now, on_add_to_tracklist = self.add_track_to_tracklist, on_pause_track = self.pause_track_now, on_resume_track = self.resume_track_now, on_get_playback_state = self.get_playback_state, on_toggle_loop_song = self.toggle_loop_song, on_stop_track = self.stop_current_track, on_seek_track = self.seek_track, on_get_current_track_info = self.get_current_track_info)
    # Open the tracklist editor window.
    # Open the tracklist manager window.
    def open_create_tracklist(self):
        self.create_tracklist_app = CreateTracklist(tk.Toplevel(self.window), self.library, theme_mode = self.theme_mode)
    # Open the track rating editor window.
    # Open the rating editor window.
    def open_update_tracks(self):
        UpdateTracks(tk.Toplevel(self.window), self.library, theme_mode = self.theme_mode)
    # Save state and shut down the app cleanly.
    # Save state and close the app cleanly.
    def on_close(self):
        self.library.save_lib_state(self.state_file)
        font.save_theme_mode(self.settings_file, self.theme_mode)
        self.window.destroy()
    # Update the theme and save it for the next session.
    # Update the theme and save the selection for later sessions.
    def set_theme(self, mode):
        self.theme_mode = mode
        font.set_theme_mode(mode)
        font.save_theme_mode(self.settings_file, mode)
        

        if mode == "System":
            font.apply_device_theme(self.window)
        else:
            font.apply_theme(self.window, mode)
    
    # Expose the current playback state to the viewer window.
    # Return the current playback state to the viewer window.
    def get_playback_state(self):
        return self.is_playing, self.is_paused
    
    # Play a track through the shared library and update playback state.
    # Play a selected track and update the shared playback state.
    def play_track_now(self, track_number, start_seconds = 0.0):
        if not track_number:
            return False
        
        if track_number.isdigit():
            track_number = track_number.zfill(2)
        else:
            track_number = track_number.upper()
        
        if self.library.get_name(track_number) is None:
            return False
        
        played = self.library.play_track(track_number, loop = self.song_loop, start_seconds = start_seconds)
        if played:
            self.library.increment_play_count(track_number)
            self.is_playing = True
            self.is_paused = False
            self.tracklist_playing = False
            self.current_track_number = track_number 
            self.current_track_length = self.library.get_track_length(track_number)
            self.current_track_offset = max(0.0, float(start_seconds))
        return played
    

    

    
    # Stop playback and clear the current track state.
    # Stop playback and clear the active track state.
    def stop_current_track(self):
        self.library.stop_track()
        self.is_playing = False
        self.is_paused = False
        self.tracklist_playing = False
        self.playback_mode = None
        self.current_track_number = None
        self.current_track_length = 0.0
        self.current_track_offset = 0.0
        self.current_index = -1
        return True
    

    

    

    

    
    # Pause the current track if one is active.
    # Pause the active track if one is currently playing.
    def pause_track_now(self):
        if not self.is_playing:
            return False
        
        if self.library.pause_track():
            self.is_playing = False
            self.is_paused = True
            return True
        return False
    

    
    

    # Resume playback after a pause.
    # Resume playback after a pause.
    def resume_track_now(self):
        if not self.is_paused:
            return False
        
        if self.library.resume_track():
            self.is_playing = True
            self.is_paused = False
            return True
        return False
    
    

    
    # Toggle looping for the current single track.
    # This flips a simple on/off flag that controls whether one track repeats.
    # Toggle looping for the current single track.
    def toggle_song_loop(self):
        self.song_loop = not self.song_loop
        return self.song_loop
    
    

    
    # Add a selected track to the shared tracklist window.
    # This opens the tracklist window if needed, checks for duplicates, and saves the updated list.
    # Add a selected track to the shared tracklist window.
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
    
    # Toggle single-track looping from the viewer window.
    # This helper is shared with the viewer so both windows control the same loop setting.
    # Toggle looping for the single-track player from the viewer window.
    def toggle_loop_song(self):
        self.song_loop = not self.song_loop
        return self.song_loop
    
    # Return the active track metadata for the viewer progress bar.
    # The viewer uses this to keep the seek slider and time label aligned with playback.
    # Return the active track information for the seekable progress slider.
    def get_current_track_info(self):
        return self.current_track_number, self.current_track_length, self.current_track_offset
    
    # Restart the current track from a new seek position.
    # The viewer calls this when the user releases the progress slider after dragging.
    # Restart the active track from a new seek position.
    def seek_track(self, seek_seconds):
        if self.current_track_number is None or self.current_track_length <= 0:
            return False
        
        seek_seconds = max(0.0, min(float(seek_seconds), self.current_track_length))

        played = self.library.play_track(self.current_track_number, loop = self.song_loop, start_seconds = seek_seconds)

        if not played:
            return False
        
        self.is_playing = True
        self.is_paused = False
        self.current_track_offset = seek_seconds
        self.current_track_length = self.library.get_track_length(self.current_track_number)
        return True
    

        

        
   

class LoginWindow:
    # Login form shown before the user can enter the main application.
    # This window is shown first and only opens the main app after successful login.
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
    
    # Validate the login credentials and open the main app if they match.
    # The credentials are intentionally simple because this is a coursework demo app.
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

# Apply the theme that was saved in the previous session to a new window.
def apply_saved_theme(window):
    theme_mode = font.load_theme_mode(settings_file)
    if theme_mode == "System":
        font.apply_device_theme(window)
    else:
        font.apply_theme(window, theme_mode)

# Create and launch the main application window after login succeeds.
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



# Create and launch the login window when the user is not already logged in.
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




# Start the correct entry point depending on whether a session file already exists.
if __name__ == "__main__":
    if session_exists():
        launch_main_app()
    else:
        launch_login()
