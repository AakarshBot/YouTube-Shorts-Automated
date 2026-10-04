from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import re

from gnews import GNews

GENRES = {
    "Cricket — India / Pakistan / Sri Lanka / Asia": {
        "India": [
            ("IN", '"cricket" India when:1d'),
        ],
        "Pakistan": [
            ("PK", '"cricket" Pakistan when:1d'),
        ],
        "Sri Lanka": [
            ("LK", '"cricket" Sri Lanka when:1d'),
        ],
        "Bangladesh": [
            ("BD", '"cricket" Bangladesh when:1d'),
        ],
        "Afghanistan": [
            ("AF", '"cricket" Afghanistan when:1d'),
        ],
    },
    "Cricket — Global": {
        "Australia": [
            ("AU", '"cricket" Australia when:1d'),
        ],
        "England": [
            ("GB", '"cricket" England when:1d'),
        ],
        "South Africa": [
            ("ZA", '"cricket" South Africa when:1d'),
        ],
        "New Zealand": [
            ("NZ", '"cricket" New Zealand when:1d'),
        ],
        "Ireland": [
            ("IE", '"cricket" Ireland when:1d'),
        ],
        "Zimbabwe": [
            ("ZW", '"cricket" Zimbabwe when:1d'),
        ],
    },
    "Niche Sports — Global": {
        "Football": [("GB", "football soccer Premier League Champions League when:1d")],
        "Tennis": [("GB", "tennis ATP WTA Grand Slam when:1d")],
        "Basketball": [("US", "basketball NBA WNBA FIBA when:1d")],
        "Athletics": [("US", "athletics track field latest record when:1d")],
        "Motorsport": [("GB", "Formula 1 F1 MotoGP motorsport when:1d")],
        "Badminton": [("MY", "badminton BWF latest when:1d")],
        "Hockey": [("CA", "ice hockey NHL latest when:1d")],
        "Golf": [("US", "golf PGA LPGA latest when:1d")],
        "Boxing": [("US", "boxing latest title fight comeback when:1d")],
        "Wrestling": [("US", "wrestling WWE latest when:1d")],
        "Swimming": [("AU", "swimming world record latest when:1d")],
        "Rugby": [("NZ", "rugby union rugby league latest when:1d")],
        "Volleyball": [("JP", "volleyball latest world championship when:1d")],
        "Cycling": [("FR", "cycling Tour de France latest when:1d")],
        "Baseball": [("US", "baseball MLB latest when:1d")],
        "Table Tennis": [("JP", "table tennis WTT latest when:1d")],
    },
}

BAD = re.compile(
    r"\b(schedule|fixtures?|standings?|scorecard|live score|how to watch|"
    r"where to watch|predicted xi|predicted lineups?|photo gallery|quiz|"
    r"odds|recap|round[- ]up|tournament review|what we learned)\b",
    re.I,
)

CRICKET_ONLY = re.compile(
    r"\b(cricket|cricketer|wicket|innings?|batter|batsman|batsmen|bowler|"
    r"bowling|batting|stumps?|lbw|bcci|pcb|slc|icc|psl|ipl|wpl|bbl|cpl|"
    r"odi|t20|test match|one-day)\b",
    re.I,
)

def _clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()

def _url(value):
    return _clean(value).split("?")[0].rstrip("/").lower()

def fetch_topics(genre, exclude_urls=()):
    if genre not in GENRES:
        raise ValueError(f"Unknown genre: {genre}")

    blocked_urls = {_url(x) for x in exclude_urls}
    searches = [
        (label, country, query)
        for label, sources in GENRES[genre].items()
        for country, query in sources
    ]

    def fetch(search):
        label, country, query = search
        news = GNews(language="en", country=country, max_results=30, max_retries=1)
        return label, news.get_news(query)

    with ThreadPoolExecutor(max_workers=min(8, len(searches))) as pool:
        grouped = {label: [] for label in GENRES[genre]}
        seen = set(blocked_urls)
        for label, batch in pool.map(fetch, searches):
            for item in batch:
                title, url = _clean(item.get("title")), _url(item.get("url"))
                if not title or not url or url in seen or BAD.search(title):
                    continue
                if genre.startswith("Cricket") and not CRICKET_ONLY.search(title):
                    continue
                if genre.startswith("Niche") and CRICKET_ONLY.search(title):
                    continue
                try:
                    published = parsedate_to_datetime(item.get("published date", "")).astimezone(timezone.utc)
                except (TypeError, ValueError, AttributeError):
                    continue
                grouped[label].append({
                    "title": title,
                    "url": url,
                    "publisher": _clean(item.get("publisher")),
                    "published_at": published,
                })
                seen.add(url)

    if genre == "Cricket — India / Pakistan / Sri Lanka / Asia":
        fallback = [
            (label, country, query.replace("when:1d", "when:3d"))
            for label in ("India", "Pakistan", "Sri Lanka")
            if len(grouped[label]) < (20 if label == "India" else 5)
            for country, query in GENRES[genre][label]
        ]
        if fallback:
            with ThreadPoolExecutor(max_workers=min(8, len(fallback))) as pool:
                for label, batch in pool.map(fetch, fallback):
                    for item in batch:
                        title, url = _clean(item.get("title")), _url(item.get("url"))
                        if not title or not url or url in seen or BAD.search(title):
                            continue
                        if not CRICKET_ONLY.search(title):
                            continue
                        try:
                            published = parsedate_to_datetime(item.get("published date", "")).astimezone(timezone.utc)
                        except (TypeError, ValueError, AttributeError):
                            continue
                        grouped[label].append({
                            "title": title,
                            "url": url,
                            "publisher": _clean(item.get("publisher")),
                            "published_at": published,
                        })
                        seen.add(url)

    now = datetime.now(timezone.utc)
    result = []
    for label, rows in grouped.items():
        rows.sort(key=lambda x: x["published_at"], reverse=True)
        fresh = [r for r in rows if r["published_at"] >= now - timedelta(hours=24)]
        if genre == "Cricket — Global" and not fresh:
            continue
        if genre == "Niche Sports — Global" and not fresh:
            continue
        if genre == "Cricket — India / Pakistan / Sri Lanka / Asia":
            limit = 20 if label == "India" else 5
            rows = fresh if len(fresh) >= limit else [
                r for r in rows if r["published_at"] >= now - timedelta(hours=72)
            ]
        else:
            rows = fresh
        if rows:
            result.append({
                "topic": label,
                "headlines": [
                    {
                        "title": r["title"],
                        "url": r["url"],
                        "publisher": r["publisher"],
                        "published_at": r["published_at"].isoformat(),
                    }
                    for r in rows[:20]
                ],
            })

    return result
