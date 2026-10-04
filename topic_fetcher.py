from concurrent.futures import ThreadPoolExecutor
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone, timedelta
from collections import defaultdict
import re

from gnews import GNews
from gdeltdoc import GdeltDoc, Filters
from rapidfuzz import fuzz

GENRES = {
    "Cricket — India / Pakistan / Sri Lanka / Asia": [
        "cricket India Pakistan Sri Lanka Bangladesh BCCI ICC when:3d",
        "cricket Kohli Rohit Bumrah Gill Babar Pakistan Sri Lanka Bangladesh when:3d",
        "cricket record comeback injury retirement debut controversy when:3d",
        "cricket women domestic WPL Ranji U19 Asia when:3d",
    ],
    "Cricket — Global": [
        'cricket Australia England "South Africa" "New Zealand" "West Indies" Afghanistan Ireland when:3d',
        "cricket record comeback injury retirement debut controversy when:3d",
        "cricket women domestic county U19 associate when:3d",
        "cricket board rule breakthrough upset milestone when:3d",
    ],
    "Niche Sports — Global": [
        "tennis badminton athletics swimming cycling golf when:3d",
        "boxing wrestling hockey basketball volleyball kabaddi chess when:3d",
        'motorsport MotoGP "Formula 1" F1 golf tennis when:3d',
        "sports record comeback injury controversy breakthrough when:3d",
    ],
}

BAD = re.compile(
    r"\b(schedule|fixtures?|standings?|scorecard|live score|how to watch|"
    r"where to watch|predicted xi|predicted lineups?|photo gallery|quiz|"
    r"odds|recap|round[- ]up|tournament review|what we learned)\b",
    re.I,
)
STOP = {
    "the","and","for","with","from","after","before","into","over","under",
    "this","that","their","his","her","its","has","have","will","says","said",
    "news","latest","report","reports","today","official","world","championship",
    "championships","cup","league","match","matches","game","games","team",
    "teams","player","players","sports","sport","when",
}

def _clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()

def _url(value):
    return _clean(value).split("?")[0].rstrip("/").lower()

def _entity(title):
    title = _clean(title)
    phrases = re.findall(
        r"\b(?:[A-Z][a-z]+|[A-Z]{2,})(?:\s+(?:[A-Z][a-z]+|[A-Z]{2,}|[0-9]+)){1,3}\b",
        title,
    )
    phrases = [p for p in phrases if p.lower() not in {"Breaking News", "Latest News"}]
    if phrases:
        return max(phrases, key=lambda p: (len(p.split()), len(p)))
    words = [
        w.lower() for w in re.findall(r"[A-Za-z][A-Za-z'-]{2,}", title)
        if w.lower() not in STOP
    ]
    return max(words, key=len, default="Story")

def _same_story(a, b):
    return fuzz.token_set_ratio(a["title"], b["title"]) >= 90

def _google(query):
    try:
        return GNews(language="en", country="IN", max_results=100).get_news(query)
    except Exception:
        return []

def _gdelt(query):
    try:
        rows = GdeltDoc().article_search(Filters(keyword=query, timespan="3d", num_records=250))
        return [
            {
                "title": _clean(r.title),
                "url": _url(r.url),
                "publisher": _clean(r.domain),
                "published_at": datetime.strptime(r.seendate, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc),
            }
            for r in rows.itertuples()
            if _clean(r.title) and _url(r.url)
        ]
    except Exception:
        return []

def fetch_topics(genre, limit=20):
    if genre not in GENRES:
        raise ValueError(f"Unknown genre: {genre}")

    with ThreadPoolExecutor(max_workers=len(GENRES[genre])) as pool:
        raw = [item for batch in pool.map(_google, GENRES[genre]) for item in batch]

    cutoff = datetime.now(timezone.utc) - timedelta(days=3)
    rows, seen = [], set()

    for item in raw:
        title, url = _clean(item.get("title")), _url(item.get("url"))
        if not title or not url or url in seen or BAD.search(title):
            continue
        try:
            published = parsedate_to_datetime(item.get("published date", ""))
            published = published.astimezone(timezone.utc)
        except (TypeError, ValueError):
            published = datetime.now(timezone.utc)
        if published < cutoff:
            continue
        rows.append({
            "title": title,
            "url": url,
            "publisher": _clean(item.get("publisher")),
            "published_at": published,
        })
        seen.add(url)

    if len({_entity(r["title"]) for r in rows}) < limit:
        query = {
            "Cricket — India / Pakistan / Sri Lanka / Asia": "cricket India Pakistan Sri Lanka Bangladesh",
            "Cricket — Global": "international cricket",
            "Niche Sports — Global": "tennis badminton athletics swimming cycling golf boxing wrestling hockey basketball",
        }[genre]
        rows += [r for r in _gdelt(query) if r["url"] not in seen]
    
    groups = defaultdict(list)
    for row in sorted(rows, key=lambda r: r["published_at"], reverse=True):
        key = _entity(row["title"])
        if not any(_same_story(row, old) for old in groups[key]):
            groups[key].append(row)

    ranked = sorted(
        groups.items(),
        key=lambda item: (
            len(item[1]),
            len({r["publisher"] for r in item[1] if r["publisher"]}),
            -max((datetime.now(timezone.utc) - r["published_at"]).total_seconds() for r in item[1]),
        ),
        reverse=True,
    )

    return [
        {
            "topic": topic,
            "headlines": [
                {
                    "title": r["title"],
                    "url": r["url"],
                    "publisher": r["publisher"],
                    "published_at": r["published_at"].isoformat(),
                }
                for r in articles
            ],
        }
        for topic, articles in ranked[:limit]
    ]
