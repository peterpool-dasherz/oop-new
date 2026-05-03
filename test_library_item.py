from pathlib import Path  # import Path for testing audio file paths
from track_library_oop import LibraryItem  # import the newer LibraryItem class


def test_library_item_stores_values():  # check that the object stores the values passed into it
    item = LibraryItem("Shape Of You", "Ed Sheeran", 4)  # create a sample library item

    assert item.name == "Shape Of You"  # the track name should be stored exactly
    assert item.artist == "Ed Sheeran"  # the artist name should be stored exactly
    assert item.rating == 4  # the rating should be stored exactly
    assert item.play_count == 0  # play count should default to 0
    assert item.audio_path is None  # audio path should default to None


def test_stars_returns_correct_number():  # check that stars() returns the expected number of stars
    item = LibraryItem("Someone Like You", "Adele", 3)  # create a track with rating 3

    assert item.stars() == "***"  # rating 3 should produce 3 stars


def test_repr_formats_library_item():  # check that __repr__() returns a readable debug string
    audio_path = Path("/music/test_track.mp3")  # create a sample audio path
    item = LibraryItem("Another Brick in the Wall", "Pink Floyd", 5, play_count=12, audio_path=audio_path)  # create a fully populated item

    assert repr(item) == (
        "LibraryItem(name=Another Brick in the Wall, artist=Pink Floyd, rating=5, "
        "play_count=12, audio_path=/music/test_track.mp3)"
    )  # __repr__ should include all stored values
