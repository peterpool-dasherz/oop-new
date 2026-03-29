class LibraryItem:
    def __init__(self, name: str, artist: str, rating: int, play_count: int = 0):
        self.name = name
        self.artist = artist
        self.rating = rating
        self.play_count = play_count

    def __repr__(self) -> str:
        return f"LibraryItem(name={self.name}, artist={self.artist}, rating={self.rating}, play_count={self.play_count})"

    def stars(self) -> str:
        return "*" * self.rating


class TrackLibrary:
    def __init__(self):
        self.library = {
            "01": LibraryItem("Another Brick in the Wall", "Pink Floyd", 4),
            "02": LibraryItem("Stayin' Alive", "Bee Gees", 5),
            "03": LibraryItem("Highway To Hell", "AC/DC", 2),
            "04": LibraryItem("Shape Of You", "Ed Sheeran", 1),
            "05": LibraryItem("Someone Like You", "Adele", 3)
        }

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

    def _normalise_track_number(self, track_number: str) -> str:
        if track_number.isdigit():
            return track_number.zfill(2)
        else:
            return track_number

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