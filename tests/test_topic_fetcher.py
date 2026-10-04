from topic_fetcher import GENRES, _entity

def test_three_sports_genres():
    assert len(GENRES) == 3
    regional = GENRES["Cricket — India / Pakistan / Sri Lanka / Asia"]
    assert all(country in regional for country in ("IN", "PK", "LK"))
    assert sum(len(queries) for queries in regional.values()) >= 8
    assert all(sum(len(queries) for queries in desk.values()) >= 8 for desk in GENRES.values())

def test_entity():
    assert _entity("Virat Kohli scores another century") == "Virat Kohli"
