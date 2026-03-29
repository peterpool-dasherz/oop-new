import track_library_oop as lib

def test_get_name_validation():
    library = lib.TrackLibrary()
    assert library.get_name("01") == "Another Brick in the Wall"

def test_get_and_set_rating():
    library = lib.TrackLibrary()
    original = library.get_rating("01")
    assert library.set_rating("03", 5) is True
    assert library.get_rating("03") == 5
    library.set_rating("03", original)

def test_increment_play_count():
    library = lib.TrackLibrary()
    before = library.get_play_count("02")
    assert library.increment_play_count("02") is True
    assert library.get_play_count("02") == before + 1