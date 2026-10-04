from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from collections import defaultdict
import re

from gnews import GNews

GENRES = {
    "Cricket — India / Pakistan / Sri Lanka / Asia": [
        "cricket India Pakistan Sri Lanka Bangladesh BCCI ICC when:3d",
        "cricket Kohli Rohit Bumrah Gill Babar Pakistan Sri Lanka Bangladesh when:3d",
        "cricket India Pakistan Sri Lanka Bangladesh record milestone when:3d",
        "cricket India Pakistan Sri Lanka Bangladesh injury comeback retirement debut when:3d",
        "cricket India Pakistan Sri Lanka Bangladesh women WPL Ranji U19 when:3d",
        "cricket India Pakistan Sri Lanka Bangladesh controversy statement reaction when:3d",
        "cricket Nepal Oman UAE Afghanistan Zimbabwe cricket when:3d",
        "cricket board rule technology breakthrough upset milestone when:3d",
    ],
    "Cricket — Global": [
        'cricket Australia England "South Africa" "New Zealand" "West Indies" Afghanistan Ireland when:3d',
        "international cricket latest when:3d",
        "cricket record milestone fastest youngest historic when:3d",
        "cricket injury comeback retirement debut dropped recalled when:3d",
        "cricket controversy statement reaction ban suspension when:3d",
        "cricket women domestic county U19 associate when:3d",
        "cricket Nepal Oman UAE Zimbabwe Namibia Scotland Ireland when:3d",
        "cricket board rule technology breakthrough upset milestone when:3d",
    ],
    "Niche Sports — Global": [
        "tennis badminton athletics swimming cycling golf when:3d",
        "boxing wrestling hockey basketball volleyball kabaddi chess when:3d",
        'motorsport MotoGP "Formula 1" F1 when:3d',
        "tennis badminton golf record milestone historic when:3d",
        "athletics swimming cycling record breakthrough upset when:3d",
        "boxing wrestling hockey controversy comeback retirement injury when:3d",
        "basketball volleyball kabaddi chess breakthrough upset controversy when:3d",
        "sports record comeback injury retirement debut controversy when:3d",
    ],
}

BAD = re.compile(
    r"\b(schedule|fixtures?|standings?|scorecard|live score|how to watch|"
    r"where to watch|predicted xi|predicted lineups?|photo gallery|quiz|"
    r"odds|recap|round[- ]up|tournament review|what we learned)\b",
    re.I,
)

STOP = {
    "the","and","for","with","from","after","before","into","over","under","this","that",
    "their","his","her","its","has","have","will","says","said","news","latest","report",
    "reports","today","official","world","championship","championships","cup","league",
    "match","matches","game","games","team","teams","player","players","sports","sport",
    "when",
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
    phrases = [p for p in phrases if p.lower() not in {"breaking news", "latest news"}]
    if phrases:
        return max(phrases, key=lambda p: (len(p.split()), len(p)))
    words = [
        w.lower() for w in re.findall(r"[A-Za-z][A-Za-z'-]{2,}", title)
        if w.lower() not in STOP
    ]
    return max(words, key=len, default="Story")

def _same_story(a, b):
    a = {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z'-]{2,}", _clean(a["title"])) if w.lower() not in STOP}
    b = {w.lower() for w in re.findall(r"[A-Za-z][A-Za-z'-]{2,}", _clean(b["title"])) if w.lower() not in STOP}
    return bool(a and b) and len(a & b) / min(len(a), len(b)) >= 0.7

def fetch_topics(genre, limit=20):
    if genre not in GENRES:
        raise ValueError(f"Unknown genre: {genre}")

    gnews = GNews(language="en", country="IN", max_results=100)
    with ThreadPoolExecutor(max_workers=len(GENRES[genre])) as pool:
        raw = [item for batch in pool.map(gnews.get_news, GENRES[genre]) for item in batch]

    now = datetime.now(timezone.utc)
    rows, seen = [], set()
    for item in raw:
        title, url = _clean(item.get("title")), _url(item.get("url"))
        if not title or not url or url in seen or BAD.search(title):
            continue
        try:
            published = parsedate_to_datetime(item.get("published date", "")).astimezone(timezone.utc)
        except (TypeError, ValueError, AttributeError):
            continue
        rows.append({
            "title": title,
            "url": url,
            "publisher": _clean(item.get("publisher")),
            "published_at": published,
        })
        seen.add(url)

    recent = [r for r in rows if r["published_at"] >= now - timedelta(hours=24)]
    if len({_entity(r["title"]) for r in recent}) >= limit:
        rows = recent

    groups = defaultdict(list)
    for row in sorted(rows, key=lambda r: r["published_at"], reverse=True):
        key = _entity(row["title"])
        if not any(_same_story(row, old) for old in groups[key]):
            groups[key].append(row)

    ranked = sorted(
        groups.items(),
        key=lambda item: (
            max(r["published_at"] for r in item[1]),
            len({r["publisher"] for r in item[1] if r["publisher"]}),
            len(item[1]),
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
