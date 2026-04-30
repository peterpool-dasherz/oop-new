import tkinter as tk
from tkinter import ttk
from pathlib import Path
import font_manager as font
import track_library_oop as lib


class UpdateTracks:
    # Window for updating the rating of an existing track.
    def __init__(self, window, library = None, theme_mode = "System"):
        self.window = window  # store the Tk window used by the editor
        self.window.title("Update Track Rating")  # set the window title
        self.window.geometry("760x420")  # set the default editor size
        self.library = library or lib.TrackLibrary()  # use the shared library if one was supplied
        self.track_input = tk.StringVar()  # store the entered track number
        self.rating_input = tk.StringVar()  # store the entered rating
        self.status_text = tk.StringVar(value = "Please enter track number and rating to update (tracks are rated from 1 to 5)")  # show the initial help message
        
        self.theme_mode = theme_mode  # remember the selected theme

        form = ttk.LabelFrame(window, text = "Update Rating", padding = 12)  # container for the input form
        form.pack(fill = "x", padx = 12, pady = (12, 8))  # place the form near the top of the window

        ttk.Label(form, text = "Track Number").grid(row = 0, column = 0, sticky = "w")  # label the track number field
        ttk.Entry(form, width = 10, textvariable = self.track_input).grid(row = 0, column = 1, padx = (6, 18))  # track number input field
        ttk.Label(form, text = "New Rating").grid(row = 0, column = 2, sticky = "w")  # label the rating field
        ttk.Entry(form, width = 10, textvariable = self.rating_input).grid(row = 0, column = 3, padx = (6, 18))  # rating input field
        ttk.Button(form, text = "Update Track Rating", command = self.update_track).grid(row = 0, column = 4)  # submit button

        self.output = tk.Text(window, width = 64, height = 12, bg = "#31384a", fg = "#e7eaf0", insertbackground = "#e7eaf0", selectbackground = "#5f8fbe")  # output area for updated track info
        self.output.pack(fill = "both", expand = True, padx = 12, pady = (0, 6))  # let the output area fill the remaining space
        self.set_text(self.output, "")  # start with an empty output panel
        status_label = ttk.Label(window, textvariable = self.status_text, padding = (12, 6)).pack(fill = "x")  # bottom status message area

        if self.theme_mode == "System":  # use the system theme if requested
            font.apply_device_theme(self.window)  # apply the OS theme
        else:
            font.apply_theme(self.window, self.theme_mode)  # apply the chosen theme

    # Replace all text in a Tk text widget with new content.
    def set_text(self, text_area, content):
        text_area.configure(state = "normal")  # unlock the widget so text can be changed
        text_area.delete("1.0", tk.END)  # remove all existing text
        text_area.insert("1.0", content)  # insert the new content at the start of the widget
        text_area.configure(state = "disabled")  # lock the widget again so the user cannot edit it directly
    
    # Validate the inputs and update the selected track's rating.
    def update_track(self):
        raw_track = self.track_input.get().strip()  # read the track number input
        raw_rating = self.rating_input.get().strip()  # read the rating input
        if not raw_rating.isdigit() or not (1 <= int(raw_rating) <= 5):  # validate the rating range
            self.status_text.set("Invalid rating. Please enter a number from 1 to 5.")  # show an error if the rating is invalid
            return  # stop here because the rating cannot be used
        track_number = raw_track.strip()  # copy the entered track number
        if track_number.isdigit():  # pad numeric track numbers to the expected format
            track_number = track_number.zfill(2)  # make numbers like 1 become 01
        else:
            track_number = track_number.upper()  # normalize custom track IDs to uppercase
        
        name = self.library.get_name(track_number)  # look up the track name in the library
        if name is None:  # stop if the track does not exist
            self.status_text.set("No track found with the given track number.")  # show an error message
            return  # do not try to update a missing track
        
        self.library.set_rating(track_number, int(raw_rating))  # save the new rating to the library
        artist = self.library.get_artist(track_number)  # read the artist for display
        plays = self.library.get_play_count(track_number)  # read the play count for display

        self.set_text(
            self.output,
            f"Updated rating for track {track_number}:\n\nName: {name}\nArtist: {artist}\nRating: {raw_rating}\nPlay Count: {plays}"  # show the updated track summary
        )
        self.status_text.set(f"Successfully updated rating for track {track_number} to {raw_rating}.")  # confirm the successful update
            

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
