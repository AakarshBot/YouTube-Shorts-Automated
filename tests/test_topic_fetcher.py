from topic_fetcher import GENRES, _entity

def test_three_sports_genres():
    assert len(GENRES) == 3
    assert all(len(queries) >= 8 for queries in GENRES.values())

def test_entity():
    assert _entity("Virat Kohli scores another century") == "Virat Kohli"
