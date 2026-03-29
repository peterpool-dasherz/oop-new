import track_library_oop as lib

def get_name_validaton():
    assert lib.get_name("01") == "Another Brick in the Wall"
def test_get_and_set_rating():
    original = lib.get_rating("01")
    assert lib.get_rating("03", 5) is True
    assert lib.get_rating("03") == 5
    lib.set_rating("03", original)
def test_increment_play_count():
    before = lib.get_play_count("02")
    assert lib.increment_play_count("02") is True
    assert lib.get_play_count("02") == before + 1
    