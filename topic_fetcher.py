from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import re

from gnews import GNews

GENRES = {
    "Cricket — India / Pakistan / Sri Lanka / Asia": {
        "IN": [
            "cricket India BCCI latest when:3d",
            "cricket Virat Kohli Rohit Sharma Bumrah Gill when:3d",
            "cricket India women domestic U19 milestone injury comeback when:3d",
            "India cricket controversy statement selection record when:3d",
        ],
        "PK": [
            "cricket Pakistan PCB Babar Azam Shaheen Afridi Rizwan when:3d",
            "Pakistan cricket women domestic PSL milestone injury comeback when:3d",
            "Pakistan cricket selection controversy statement record when:3d",
        ],
        "LK": [
            "cricket Sri Lanka SLC Hasaranga Mendis Nissanka when:3d",
            "Sri Lanka cricket women domestic milestone injury comeback when:3d",
            "Sri Lanka cricket selection controversy statement record when:3d",
        ],
        "BD": ["Bangladesh cricket BCB latest milestone injury controversy when:3d"],
        "AF": ["Afghanistan cricket ACB latest milestone injury controversy when:3d"],
    },
    "Cricket — Global": {
        "AU": [
            "cricket Australia latest player record injury controversy when:3d",
            "Australia cricket women domestic milestone comeback when:3d",
        ],
        "GB": [
            "cricket England latest player record injury controversy when:3d",
            "England cricket women county milestone comeback when:3d",
        ],
        "ZA": [
            "cricket South Africa latest player record injury controversy when:3d",
            "South Africa cricket women domestic milestone comeback when:3d",
        ],
        "NZ": [
            "cricket New Zealand latest player record injury controversy when:3d",
            "New Zealand cricket women domestic milestone comeback when:3d",
        ],
    },
    "Niche Sports — Global": {
        "US": [
            "tennis basketball golf swimming athletics latest record when:3d",
            "boxing wrestling hockey volleyball latest comeback controversy when:3d",
        ],
        "GB": [
            "tennis athletics cycling golf latest record historic when:3d",
            "motorsport Formula 1 boxing hockey latest comeback when:3d",
        ],
        "AU": [
            "tennis swimming cycling motorsport latest record when:3d",
            "rugby hockey basketball latest milestone controversy when:3d",
        ],
        "JP": [
            "tennis badminton motorsport golf latest record when:3d",
            "boxing wrestling swimming athletics latest milestone when:3d",
        ],
    },
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

def fetch_topics(genre, limit=20, exclude_topics=(), exclude_urls=()):
    if genre not in GENRES:
        raise ValueError(f"Unknown genre: {genre}")

    blocked_topics = {str(x).casefold() for x in exclude_topics}
    blocked_urls = {_url(x) for x in exclude_urls}
    searches = [
        (country, GNews(language="en", country=country, max_results=100), query)
        for country, queries in GENRES[genre].items()
        for query in queries
    ]

    with ThreadPoolExecutor(max_workers=len(searches)) as pool:
        futures = [pool.submit(news.get_news, query) for _, news, query in searches]
        raw = [
            {**item, "_country": country}
            for (country, _, _), future in zip(searches, futures)
            for item in future.result()
        ]

    now = datetime.now(timezone.utc)
    rows, seen = [], set()
    for item in raw:
        title, url = _clean(item.get("title")), _url(item.get("url"))
        if not title or not url or url in seen or url in blocked_urls or BAD.search(title):
            continue
        topic = _entity(title)
        if any(key in topic.casefold() or topic.casefold() in key for key in blocked_topics):
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
            "topic": topic,
            "country": item["_country"],
        })
        seen.add(url)

    recent = [r for r in rows if r["published_at"] >= now - timedelta(hours=24)]
    if len({r["topic"].casefold() for r in recent}) >= limit:
        rows = recent

    groups = []
    for row in sorted(rows, key=lambda r: r["published_at"], reverse=True):
        topic = row["topic"]
        key = topic.casefold()
        group = next(
            (g for g in groups if key == g["key"] or key in g["key"] or g["key"] in key),
            None,
        )
        if group:
            group["headlines"].append(row)
            group["countries"].add(row["country"])
        else:
            groups.append({"topic": topic, "key": key, "headlines": [row], "countries": {row["country"]}})

    ranked = sorted(
        groups,
        key=lambda group: (
            max(r["published_at"] for r in group["headlines"]),
            len({r["publisher"] for r in group["headlines"] if r["publisher"]}),
            len(group["headlines"]),
        ),
        reverse=True,
    )

    if genre == "Cricket — India / Pakistan / Sri Lanka / Asia":
        selected = []
        selected_keys = set()
        for country in ("PK", "LK"):
            for group in ranked:
                if country in group["countries"] and group["key"] not in selected_keys:
                    selected.append(group)
                    selected_keys.add(group["key"])
                    if sum(1 for x in selected if country in x["countries"]) == 3:
                        break
        selected.extend(group for group in ranked if group["key"] not in selected_keys)
        ranked = selected

    return [
        {
            "topic": group["topic"],
            "headlines": [
                {
                    "title": r["title"],
                    "url": r["url"],
                    "publisher": r["publisher"],
                    "published_at": r["published_at"].isoformat(),
                }
                for r in group["headlines"]
            ],
        }
        for group in ranked[:limit]
    ]
