from topic_fetcher import GENRES

REGIONAL = "Cricket — India / Pakistan / Sri Lanka / Asia"
GLOBAL = "Cricket — Global"
NICHE = "Niche Sports — Global"

def test_genre_structure():
    assert set(GENRES) == {REGIONAL, GLOBAL, NICHE}
    assert {"India", "Pakistan", "Sri Lanka"} <= set(GENRES[REGIONAL])
    assert {"Australia", "England", "South Africa", "New Zealand"} <= set(GENRES[GLOBAL])
    assert {"Football", "Tennis", "Basketball", "Athletics", "Motorsport", "Badminton"} <= set(GENRES[NICHE])

def test_cricket_queries_are_cricket_specific():
    for desk in (REGIONAL, GLOBAL):
        assert all('"cricket"' in query.lower() for sources in GENRES[desk].values() for _, query in sources)

def test_niche_excludes_cricket_and_covers_sports():
    assert "Cricket" not in GENRES[NICHE]
    assert len(GENRES[NICHE]) >= 15
