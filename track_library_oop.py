from pathlib import Path
import csv

try:
    import pygame
except ModuleNotFoundError:
    pygame = None


class LibraryItem:
    def __init__(self, name: str, artist: str, rating: int, play_count: int = 0, audio_path=None):
        self.name = name
        self.artist = artist
        self.rating = rating
        self.play_count = play_count
        self.audio_path = audio_path

    def __repr__(self) -> str:
        return (
            "LibraryItem("
            f"name={self.name}, artist={self.artist}, rating={self.rating}, "
            f"play_count={self.play_count}, audio_path={self.audio_path}"
            ")"
        )

    def stars(self) -> str:
        return "*" * self.rating


class TrackLibrary:
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

    def _normalise_track_number(self, track_number: str) -> str:
        if track_number.isdigit():
            return track_number.zfill(2)
        return track_number

    def get_name(self, track_number: str):
        item = self.library.get(track_number)
        return item.name if item else None

    def get_artist(self, track_number: str):
        item = self.library.get(track_number)
        return item.artist if item else None

    def get_rating(self, track_number: str):
        item = self.library.get(track_number)
        return item.rating if item else None

    def get_play_count(self, track_number: str):
        item = self.library.get(track_number)
        return item.play_count if item else -1

    def get_audio_path(self, track_number: str):
        item = self.library.get(track_number)
        if not item or not item.audio_path:
            return None
        return item.audio_path

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

    def set_rating(self, track_number: str, rating: int):
        item = self.library.get(track_number)
        if not item:
            return False
        item.rating = rating
        return True

    def increment_play_count(self, track_number: str):
        item = self.library.get(track_number)
        if not item:
            return False
        item.play_count += 1
        return True

    def _format_track(self, track_number: str, item: LibraryItem) -> str:
        return f"{track_number}: {item.name} - {item.artist} {item.stars()}"

    def list_all(self) -> str:
        lines = [self._format_track(track_number, item) for track_number, item in self.library.items()]
        return "\n".join(lines)

    def list_artists(self):
        artists = {item.artist for item in self.library.values()}
        return sorted(artists)

    def search_tracks(self, query: str) -> str:
        query = query.strip().lower()
        if not query:
            return ""
        matching_tracks = []
        for track_number, item in self.library.items():
            if query in item.name.lower() or query in item.artist.lower():
                matching_tracks.append(self._format_track(track_number, item))
        return "\n".join(matching_tracks)

    def filter_by_artist(self, artist: str) -> str:
        artist = artist.strip().lower()
        if not artist:
            return ""
        matching_artist = []
        for track_number, item in self.library.items():
            if item.artist.lower() == artist:
                matching_artist.append(self._format_track(track_number, item))
        return "\n".join(matching_artist)
    
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

    def _init_audio(self):
        if pygame is None:
            return False
        if pygame.mixer.get_init() is None:
            pygame.mixer.init()
        return True

    def play_track(self, track_number, loop = False):
        audio_path = self.get_audio_path(track_number)
        if audio_path is None or not audio_path.exists():
            return False
        if not self._init_audio():
            return False
        pygame.mixer.music.stop()
        pygame.mixer.music.load(str(audio_path))
        pygame.mixer.music.play(loops = -1 if loop else 0)
        return True

    def stop_track(self):
        if pygame is not None and pygame.mixer.get_init():
            pygame.mixer.music.stop()
    
    
    


    def pause_track(self):
        if pygame is not None and pygame.mixer.get_init():
            pygame.mixer.music.pause()
            return True
        return False
    
    def resume_track(self):
        if pygame is not None and pygame.mixer.get_init():
            pygame.mixer.music.unpause()
            return True
        return False
    



    def save_lib_state(self, csv_path):
        path = Path(csv_path)
        with path.open("w", newline = "", encoding = "utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["track_number", "name", "artist", "rating", "play_count", "audio_path"])

            for track_number, item in self.library.items():
                audio_path = str(item.audio_path) 
                if item.audio_path is None:
                    audio_path = ""
                else:
                    audio_path = str(item.audio_path)
                writer.writerow([track_number, item.name, item.artist, item.rating, item.play_count, audio_path])

    def load_lib_state(self, csv_path):
        path = Path(csv_path)
        if not path.exists():
            return 0
        loaded_count = 0
        with path.open("r", newline = "", encoding = "utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                track_number = row.get("track_number", "").strip()
                if not track_number:
                    continue
                name = row.get("name", "").strip()
                artist = row.get("artist", "").strip()
                rating_text = row.get("rating", "").strip()
                play_count_text = row.get("play_count", "").strip()
                audio_path = row.get("audio_path", "").strip()

                if rating_text.isdigit():
                    rating = int(rating_text)
                else:
                    rating = 0
                if play_count_text.isdigit():
                    play_count = int(play_count_text)
                else:
                    play_count = 0
                
                if track_number in self.library:
                    item = self.library[track_number]
                    if name is not None:
                        item.name = name
                    if artist is not None:
                        item.artist = artist
                    item.rating = rating
                    item.play_count = play_count
                    item.audio_path = Path(audio_path) if audio_path else item.audio_path
                elif name is not None and artist is not None:
                    self.add_custom_track(track_number, name, artist, audio_path, rating, play_count)
                loaded_count += 1
        return loaded_count