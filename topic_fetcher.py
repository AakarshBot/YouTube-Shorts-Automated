from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import re

from gnews import GNews

GENRES = {
    "Cricket — India / Pakistan / Sri Lanka / Asia": {
        "India": [
            ("IN", '"cricket" India latest BCCI when:3d'),
            ("IN", '"cricket" Kohli Rohit Bumrah Gill when:3d'),
            ("IN", '"cricket" India women domestic U19 when:3d'),
            ("IN", '"cricket" India record milestone injury comeback when:3d'),
        ],
        "Pakistan": [
            ("PK", '"cricket" Pakistan PCB Babar Shaheen Rizwan when:3d'),
            ("PK", '"cricket" Pakistan women domestic PSL when:3d'),
            ("PK", '"cricket" Pakistan selection controversy record when:3d'),
        ],
        "Sri Lanka": [
            ("LK", '"cricket" Sri Lanka SLC Hasaranga Mendis Nissanka when:3d'),
            ("LK", '"cricket" Sri Lanka women domestic when:3d'),
            ("LK", '"cricket" Sri Lanka selection controversy record when:3d'),
        ],
        "Bangladesh": [("BD", '"cricket" Bangladesh BCB latest milestone controversy when:3d')],
        "Afghanistan": [("AF", '"cricket" Afghanistan ACB latest milestone controversy when:3d')],
    },
    "Cricket — Global": {
        "Australia": [
            ("AU", '"cricket" Australia latest record injury controversy when:3d'),
            ("AU", '"cricket" Australia women milestone comeback when:3d'),
        ],
        "England": [
            ("GB", '"cricket" England latest record injury controversy when:3d'),
            ("GB", '"cricket" England women county milestone when:3d'),
        ],
        "South Africa": [
            ("ZA", '"cricket" South Africa latest record injury controversy when:3d'),
            ("ZA", '"cricket" South Africa women milestone when:3d'),
        ],
        "New Zealand": [
            ("NZ", '"cricket" New Zealand latest record injury controversy when:3d'),
            ("NZ", '"cricket" New Zealand women milestone when:3d'),
        ],
        "Ireland": [("IE", '"cricket" Ireland latest record injury controversy when:3d')],
        "Zimbabwe": [("ZW", '"cricket" Zimbabwe latest record injury controversy when:3d')],
    },
    "Niche Sports — Global": {
        "Football": [("GB", "football soccer Premier League Champions League when:3d")],
        "Tennis": [("GB", "tennis ATP WTA Grand Slam when:3d")],
        "Basketball": [("US", "basketball NBA WNBA FIBA when:3d")],
        "Athletics": [("US", "athletics track field latest record when:3d")],
        "Motorsport": [("GB", "Formula 1 F1 MotoGP motorsport when:3d")],
        "Badminton": [("MY", "badminton BWF latest when:3d")],
        "Hockey": [("CA", "ice hockey NHL latest when:3d")],
        "Golf": [("US", "golf PGA LPGA latest when:3d")],
        "Boxing": [("US", "boxing latest title fight comeback when:3d")],
        "Wrestling": [("US", "wrestling WWE latest when:3d")],
        "Swimming": [("AU", "swimming world record latest when:3d")],
        "Rugby": [("NZ", "rugby union rugby league latest when:3d")],
        "Volleyball": [("JP", "volleyball latest world championship when:3d")],
        "Cycling": [("FR", "cycling Tour de France latest when:3d")],
        "Baseball": [("US", "baseball MLB latest when:3d")],
        "Table Tennis": [("JP", "table tennis WTT latest when:3d")],
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
        news = GNews(language="en", country=country, max_results=100)
        return label, [
            {**item, "_country": country}
            for item in news.get_news(query)
        ]

    with ThreadPoolExecutor(max_workers=len(searches)) as pool:
        batches = pool.map(fetch, searches)
        grouped = {label: [] for label in GENRES[genre]}
        seen = set()
        for label, batch in batches:
            for item in batch:
                title, url = _clean(item.get("title")), _url(item.get("url"))
                if not title or not url or url in seen or url in blocked_urls or BAD.search(title):
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
