from datetime import datetime, timezone
from types import SimpleNamespace

import topic_fetcher
from topic_fetcher import BAD, DESK_PILLS, DESKS, GENRES, _group_india_rows

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

def test_cricket_queries_target_specific_story_signals():
    query = GENRES["Cricket — India / Pakistan / Sri Lanka / Asia"]["India"][0][1].lower()
    assert '"india cricket"' in query
    assert "bcci" in query
    assert '"records & stats"' in query
    assert "-scorecard" in query

def test_cricket_page_filter_rejects_reference_pages():
    assert BAD.search("NKP Salve Challenger Trophy, 2008/09 Cricket Team Records & Stats")
    assert BAD.search("Cricket Grounds | Afro Asia Cup, 2005")
    assert not BAD.search("West Indies beat India in record chase as Hope hits 162")

def test_india_headlines_group_by_shared_title_entity():
    rows = [
        {"title": "Virat Kohli leads India after match win", "published_at": datetime(2026, 10, 4, 10, tzinfo=timezone.utc)},
        {"title": "Kohli backed to shine again for India", "published_at": datetime(2026, 10, 4, 9, tzinfo=timezone.utc)},
        {"title": "India await Asia Cup title challenge", "published_at": datetime(2026, 10, 4, 8, tzinfo=timezone.utc)},
        {"title": "Asia Cup contenders prepare for battle", "published_at": datetime(2026, 10, 4, 7, tzinfo=timezone.utc)},
        {"title": "Jasprit Bumrah returns to training", "published_at": datetime(2026, 10, 4, 6, tzinfo=timezone.utc)},
    ]
    groups = _group_india_rows(rows)
    kohli = next(group for group in groups if "kohli" in group["topic"].lower())
    asia = next(group for group in groups if "asia cup" in group["topic"].lower())
    assert len(kohli["headlines"]) == 2
    assert len(asia["headlines"]) == 2
    assert len(groups) == 3
    assert all(isinstance(row["published_at"], str) for group in groups for row in group["headlines"])


def test_fetch_topics_uses_raw_gnews_urls(monkeypatch):
    class FakeGNews:
        def __init__(self, **kwargs):
            self.max_results = kwargs["max_results"]

        def _ceid(self):
            return "&hl=en&gl=IN&ceid=IN:en"

        def _fetch_feed(self, url):
            assert "/search?q=" in url
            return SimpleNamespace(entries=[{
                "title": "India wins an important cricket match",
                "link": "https://news.google.com/rss/articles/raw-selected-story",
                "description": "GNews summary.",
                "source": "Example",
                "published": "Sun, 04 Oct 2026 10:00:00 GMT",
            }])

        def get_news(self, query):
            raise AssertionError("Topic Fetcher must not resolve URLs through get_news()")

    monkeypatch.setattr(topic_fetcher, "GNews", FakeGNews)
    result = topic_fetcher.fetch_topics("News")
    assert result[0]["headlines"][0]["url"] == "https://news.google.com/rss/articles/raw-selected-story"


def test_source_url_is_not_lowercased_or_stripped():
    from topic_fetcher import _url
    url = "https://Example.com/Story/ABC?Param=Value"
    assert _url(url) == "https://Example.com/Story/ABC?Param=Value"
