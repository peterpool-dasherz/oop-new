from pathlib import Path
import csv

try:
    import pygame
except ModuleNotFoundError:
    pygame = None


class LibraryItem:
    # Store the metadata for one track in the library.
    def __init__(self, name: str, artist: str, rating: int, play_count: int = 0, audio_path=None):
        self.name = name
        self.artist = artist
        self.rating = rating
        self.play_count = play_count
        self.audio_path = audio_path

    # Return a readable debug representation of the library item.
    def __repr__(self) -> str:
        return (
            "LibraryItem("
            f"name={self.name}, artist={self.artist}, rating={self.rating}, "
            f"play_count={self.play_count}, audio_path={self.audio_path}"
            ")"
        )

    # Convert the numeric rating into a string of star characters.
    def stars(self) -> str:
        return "*" * self.rating


class TrackLibrary:
    # Load the built-in track library and prepare the music directory path.
    def __init__(self):
        self.music_dir = Path(__file__).resolve().parent / "Music links"
        self.library = {
            "01": LibraryItem(
                "Another Brick in the Wall",
                "Pink Floyd",
                4,
                audio_path=self.music_dir / "pink floyd - another brick in the wall - Piccologollum (youtube).mp3",
            ),
            "02": LibraryItem(
                "Stayin' Alive",
                "Bee Gees",
                5,
                audio_path=self.music_dir / "Bee Gees - Stayin' Alive (Official Music Video) - BeeGeesVEVO (youtube).mp3",
            ),
            "03": LibraryItem(
                "Highway To Hell",
                "AC/DC",
                2,
                audio_path=self.music_dir / "AC_DC - Highway to Hell (Official Video) - acdcVEVO (youtube).mp3",
            ),
            "04": LibraryItem(
                "Shape Of You",
                "Ed Sheeran",
                1,
                audio_path=self.music_dir / "Ed Sheeran - Shape Of You [Official Lyric Video] - Ed Sheeran (youtube).mp3",
            ),
            "05": LibraryItem(
                "Someone Like You",
                "Adele",
                3,
                audio_path=self.music_dir / "Adele - Someone Like You (Official Music Video) - Adele (youtube).mp3",
            ),
        }

    # Normalize track numbers so the UI and stored library keys match.
    def _normalise_track_number(self, track_number: str) -> str:
        if track_number.isdigit():
            return track_number.zfill(2)
        return track_number

    # Return the stored track name for a given track number.
    def get_name(self, track_number: str):
        item = self.library.get(track_number)
        return item.name if item else None

    # Return the stored artist for a given track number.
    def get_artist(self, track_number: str):
        item = self.library.get(track_number)
        return item.artist if item else None

    # Return the stored rating for a given track number.
    def get_rating(self, track_number: str):
        item = self.library.get(track_number)
        return item.rating if item else None

    # Return the stored play count for a given track number.
    def get_play_count(self, track_number: str):
        item = self.library.get(track_number)
        return item.play_count if item else -1

    # Return the audio file path for a given track number if one exists.
    def get_audio_path(self, track_number: str):
        item = self.library.get(track_number)
        if not item or not item.audio_path:
            return None
        return item.audio_path

    # Add a custom track to the library and store its metadata.
    def add_custom_track(self, track_number: str, name: str, artist: str, audio_path: str = "", rating: int = 0, play_count: int = 0):
        track_number = self._normalise_track_number(track_number)
        self.library[track_number] = LibraryItem(
            name,
            artist,
            rating,
            play_count=play_count,
            audio_path=Path(audio_path) if audio_path else None,
        )
        return track_number

    # Update the rating value for one track.
    def set_rating(self, track_number: str, rating: int):
        item = self.library.get(track_number)
        if not item:
            return False
        item.rating = rating
        return True

    # Increase the play count after successful playback.
    def increment_play_count(self, track_number: str):
        item = self.library.get(track_number)
        if not item:
            return False
        item.play_count += 1
        return True

    # Format one track for display in the UI track list.
    def _format_track(self, track_number: str, item: LibraryItem) -> str:
        return f"{track_number}: {item.name} - {item.artist} {item.stars()}"

    # Return every track in the library as a formatted text block.
    def list_all(self) -> str:
        lines = [self._format_track(track_number, item) for track_number, item in self.library.items()]
        return "\n".join(lines)

    # Return a sorted list of unique artist names.
    def list_artists(self):
        artists = {item.artist for item in self.library.values()}
        return sorted(artists)

    # Search tracks by matching the query against the track name or artist.
    def search_tracks(self, query: str) -> str:
        query = query.strip().lower()
        if not query:
            return ""
        matching_tracks = []
        for track_number, item in self.library.items():
            if query in item.name.lower() or query in item.artist.lower():
                matching_tracks.append(self._format_track(track_number, item))
        return "\n".join(matching_tracks)

    # Return only the tracks that belong to one artist.
    def filter_by_artist(self, artist: str) -> str:
        artist = artist.strip().lower()
        if not artist:
            return ""
        matching_artist = []
        for track_number, item in self.library.items():
            if item.artist.lower() == artist:
                matching_artist.append(self._format_track(track_number, item))
        return "\n".join(matching_artist)
    
    # Load custom tracks from a saved CSV file if it exists.
    def load_custom_tracks_from_csv(self, csv_path: str):
        path = Path(csv_path)
        if not path.exists():
            return 0
        loaded_count = 0
        with path.open("r", newline = "", encoding = "utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                track_number = row.get("track_number", "").strip()
                if not track_number.upper().startswith("CUST"):
                    continue
                name = row.get("name", "").strip()
                artist = row.get("artist", "").strip()
                audio_path = row.get("audio_path", "").strip()

                if not track_number or not name or not artist:
                    continue
                self.add_custom_track(track_number, name, artist, audio_path)
                loaded_count += 1
        return loaded_count
    
    # Combine text search and artist filtering into one result.
    def search_and_filter(self, query: str, artist: str) -> str:
        query = query.strip().lower()
        artist = artist.strip().lower()
        results = []

        for track_number, item in self.library.items():
            if artist != "all artists" and item.artist.lower() != artist:
                continue
            if query and (query not in item.name.lower()) and (query not in item.artist.lower()):
                continue
            results.append(self._format_track(track_number, item))
        return "\n".join(results)

    # Initialize pygame audio only when playback is needed.
    def _init_audio(self):
        if pygame is None:
            return False
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
        return True

    # Load and play a track, optionally looping and optionally starting partway through.
    def play_track(self, track_number, loop = False, start_seconds = 0.0):
        audio_path = self.get_audio_path(track_number)
        if audio_path is None or not audio_path.exists():
            return False
        if not self._init_audio():
            return False
        
        pygame.mixer.music.stop()
        pygame.mixer.music.load(str(audio_path))

        start_seconds = max(0.0, float(start_seconds))
        if start_seconds > 0:
            if loop:
                pygame.mixer.music.play(loops = -1, start = start_seconds)
            else:
                pygame.mixer.music.play(loops = 0, start = start_seconds)
        else:
            if loop:
                pygame.mixer.music.play(loops = -1)
            else:
                pygame.mixer.music.play(loops = 0)
        return True
    




    # Stop the currently playing track.
    def stop_track(self):
        if pygame is not None and pygame.mixer.get_init():
            pygame.mixer.music.stop()
    
    


    # Pause playback without resetting the current position.
    def pause_track(self):
        if pygame is not None and pygame.mixer.get_init():
            pygame.mixer.music.pause()
            return True
        return False
    
    # Resume a paused track from its current position.
    def resume_track(self):
        if pygame is not None and pygame.mixer.get_init():
            pygame.mixer.music.unpause()
            return True
        return False
    
    # Read the track length so the UI can draw accurate progress displays.
    def get_track_length(self, track_number: str):
        audio_path = self.get_audio_path(track_number)
        if audio_path is None or not audio_path.exists():
            return 0.0
        
        try:
            if pygame is None:
                return 0.0
            return pygame.mixer.Sound(str(audio_path)).get_length()
        except Exception:
            return 0.0   



    # Save the full library state to disk.
    def save_lib_state(self, csv_path):
        path = Path(csv_path)  # convert the path-like value into a Path object
        with path.open("w", newline = "", encoding = "utf-8") as file:  # open the file for writing CSV data
            writer = csv.writer(file)  # create a CSV writer for the output file
            writer.writerow(["track_number", "name", "artist", "rating", "play_count", "audio_path"])  # write the CSV header row

            for track_number, item in self.library.items():  # loop through every track in the library
                audio_path = str(item.audio_path)  # convert the stored path into text
                if item.audio_path is None:  # if the track has no audio file path
                    audio_path = ""  # store an empty string in the CSV
                else:  # otherwise
                    audio_path = str(item.audio_path)  # keep the audio file path as text
                writer.writerow([track_number, item.name, item.artist, item.rating, item.play_count, audio_path])  # write one track record to the CSV

    def load_lib_state(self, csv_path):
        path = Path(csv_path)  # convert the file path into a Path object
        if not path.exists():  # stop if the saved file does not exist
            return 0  # report that nothing was loaded
        loaded_count = 0  # count how many rows were restored
        with path.open("r", newline = "", encoding = "utf-8") as file:  # open the CSV for reading
            reader = csv.DictReader(file)  # read each row by column name
            for row in reader:  # process each saved track row
                track_number = row.get("track_number", "").strip()  # read the track number column
                if not track_number:  # skip empty rows
                    continue  # move on to the next row
                name = row.get("name", "").strip()  # read the track name
                artist = row.get("artist", "").strip()  # read the artist name
                rating_text = row.get("rating", "").strip()  # read the saved rating as text
                play_count_text = row.get("play_count", "").strip()  # read the saved play count as text
                audio_path = row.get("audio_path", "").strip()  # read the saved audio path

                if rating_text.isdigit():  # convert the rating if it is numeric
                    rating = int(rating_text)  # store the rating as an integer
                else:
                    rating = 0  # fall back to zero if the value is missing or invalid
                if play_count_text.isdigit():  # convert the play count if it is numeric
                    play_count = int(play_count_text)  # store the play count as an integer
                else:
                    play_count = 0  # fall back to zero if the value is missing or invalid
                
                if track_number in self.library:  # update an existing built-in or custom track
                    item = self.library[track_number]  # retrieve the stored item
                    if name is not None:  # update the name if the CSV contains one
                        item.name = name  # overwrite the stored track name
                    if artist is not None:  # update the artist if the CSV contains one
                        item.artist = artist  # overwrite the stored artist name
                    item.rating = rating  # restore the saved rating
                    item.play_count = play_count  # restore the saved play count
                    item.audio_path = Path(audio_path) if audio_path else item.audio_path  # restore the saved audio path if one exists
                elif name is not None and artist is not None:  # create a custom track if it does not already exist
                    self.add_custom_track(track_number, name, artist, audio_path, rating, play_count)  # add the missing track to the library
                loaded_count += 1  # count this row as restored
        return loaded_count  # report how many rows were loaded
