from topic_fetcher import DESK_PILLS, DESKS, GENRES

SPORTS = "Sports"
NON_SPORTS = (
    "News",
    "Entertainment",
    "Technology",
    "Business & Finance",
    "Gaming",
    "Science & Space",
)

def test_deep_dive_desks():
    assert tuple(DESKS) == (SPORTS,) + NON_SPORTS
    assert set(DESKS[SPORTS]) == set(GENRES)
    assert all(DESKS[desk] == tuple(DESK_PILLS[desk]) for desk in NON_SPORTS)

def test_non_sports_have_focused_pills():
    assert all(len(DESK_PILLS[desk]) == 4 for desk in NON_SPORTS)
    assert all(len(sources) == 1 for desk in NON_SPORTS for sources in DESK_PILLS[desk].values())

def test_sports_and_niche_structure():
    regional = "Cricket — India / Pakistan / Sri Lanka / Asia"
    global_ = "Cricket — Global"
    niche = "Niche Sports — Global"
    assert {"India", "Pakistan", "Sri Lanka", "Bangladesh", "Afghanistan"} <= set(GENRES[regional])
    assert {"Australia", "England", "South Africa", "New Zealand"} <= set(GENRES[global_])
    assert "Cricket" not in GENRES[niche]
    assert len(GENRES[niche]) >= 15

def test_cricket_queries_are_cricket_specific():
    for desk in ("Cricket — India / Pakistan / Sri Lanka / Asia", "Cricket — Global"):
        assert all('"cricket"' in query.lower() for sources in GENRES[desk].values() for _, query in sources)
