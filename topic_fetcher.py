from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
import re

from gnews import GNews
from gdeltdoc import GdeltDoc, Filters
from rapidfuzz import fuzz

GENRES = {
    "Cricket — India / Pakistan / Sri Lanka / Asia": (
        '(cricket India Pakistan "Sri Lanka" Bangladesh BCCI ICC) when:3d',
        '(cricket Kohli Rohit Bumrah Gill Babar Pakistan Sri Lanka Bangladesh) when:3d',
        '(cricket record comeback injury retirement debut controversy) when:3d',
        '(cricket women domestic WPL Ranji U19 Asia) when:3d',
    ),
    "Cricket — Global": (
        'cricket Australia England "South Africa" "New Zealand" "West Indies" Afghanistan Ireland when:3d',
        'cricket record comeback injury retirement debut controversy global when:3d',
        'cricket women domestic county U19 associate when:3d',
        'cricket board rule breakthrough upset milestone when:3d',
    ),
    "Niche Sports — Global": (
        'tennis badminton athletics swimming cycling golf when:3d',
        'boxing wrestling hockey basketball volleyball kabaddi chess when:3d',
        'motorsport MotoGP "Formula 1" F1 golf tennis when:3d',
        'niche sports record comeback injury controversy breakthrough when:3d',
    ),
}

UTILITY = re.compile(
    r"\b(schedule|fixtures?|standings?|scorecard|live score|how to watch|"
    r"where to watch|predicted xi|predicted lineup|photo gallery|quiz|"
    r"transfer rumours?|odds)\b",
    re.I,
)
STALE = re.compile(
    r"\b(recap|review|highlights?|full results?|reaction to final|"
    r"post-match|after the final|tournament review)\b",
    re.I,
)
STOP = {
    "the","and","for","with","from","after","before","into","over","under",
    "this","that","their","his","her","its","has","have","will","says","said",
    "news","latest","report","reports","today","official","world","championship",
    "championships","cup","league","match","matches","game","games","team",
    "teams","player","players","sports","sport",
}

def _clean(s): return re.sub(r"\s+", " ", str(s or "")).strip()

def _url(s):
    return _clean(s).split("?")[0].rstrip("/").lower()

def _tokens(s):
    return {x.lower() for x in re.findall(r"[A-Za-z][A-Za-z'-]{2,}", _clean(s)) if x.lower() not in STOP}

def _entity(title):
    title = _clean(title)
    phrases = re.findall(r"\b(?:[A-Z][a-z]+|[A-Z]{2,})(?:\s+(?:[A-Z][a-z]+|[A-Z]{2,}|[0-9]+)){1,3}\b", title)
    phrases = [p.strip() for p in phrases if p.lower() not in {"breaking news","latest news"}]
    if phrases:
        return max(phrases, key=lambda p: (len(p.split()), len(p)))
    words = list(_tokens(title))
    return max(words, key=len) if words else "Story"

def _same_event(a, b):
    return _url(a["url"]) == _url(b["url"]) or (
        fuzz.token_set_ratio(a["title"], b["title"]) >= 88
        and len(_tokens(a["title"]) & _tokens(b["title"])) >= 3
    )

def fetch_topics(genre, limit=20):
    if genre not in GENRES:
        raise ValueError(f"Unknown genre: {genre}")

    google = GNews(language="en", country="IN", max_results=100)
    raw = []
    for query in GENRES[genre]:
        try:
            raw += google.get_news(query)
        except Exception:
            pass

    cutoff = datetime.now(timezone.utc) - timedelta(days=3)
    rows = []
    seen = set()
    for item in raw:
        url = _url(item.get("url"))
        title = _clean(item.get("title"))
        if not url or not title or url in seen or UTILITY.search(title):
            continue
        try:
            published = datetime.strptime(
                item.get("published date", ""), "%a, %d %b %Y %H:%M:%S %Z"
            ).replace(tzinfo=timezone.utc)
        except ValueError:
            published = datetime.now(timezone.utc)
        if published < cutoff or STALE.search(title):
            continue
        row = {
            "title": title,
            "url": url,
            "publisher": _clean(item.get("publisher")),
            "description": _clean(item.get("description")),
            "published_at": published,
            "entity": _entity(title),
        }
        rows.append(row)
        seen.add(url)

    groups = []
    for row in sorted(rows, key=lambda x: x["published_at"], reverse=True):
        for group in groups:
            if row["entity"].lower() == group["entity"].lower() or _same_event(row, group["articles"][0]):
                group["articles"].append(row)
                break
        else:
            groups.append({"entity": row["entity"], "articles": [row]})

    gdelt = GdeltDoc()
    counts = Counter()
    try:
        terms = " OR ".join(
            [x for x in re.findall(r"[A-Za-z]+", genre) if x.lower() not in {"cricket","global","niche","sports"}]
        )
        if terms:
            data = gdelt.article_search(Filters(keyword=terms, timespan="3d", num_records=250))
            counts.update(_url(x) for x in data["url"].dropna().tolist())
    except Exception:
        pass

    ranked = []
    for group in groups:
        articles = group["articles"]
        newest = max(a["published_at"] for a in articles)
        hours = max(0.0, (datetime.now(timezone.utc) - newest).total_seconds() / 3600)
        freshness = max(0.0, 72 - hours)
        sources = len({a["publisher"] for a in articles if a["publisher"]})
        coverage = sum(counts[_url(a["url"])] for a in articles)
        ranked.append((freshness + sources * 5 + len(articles) * 3 + min(coverage, 20), group))

    ranked.sort(key=lambda x: x[0], reverse=True)
    return [
        {
            "topic": group["entity"],
            "headlines": [
                {
                    "title": a["title"],
                    "url": a["url"],
                    "publisher": a["publisher"],
                    "published_at": a["published_at"].isoformat(),
                }
                for a in sorted(group["articles"], key=lambda x: x["published_at"], reverse=True)
            ],
        }
        for _, group in ranked[:limit]
    ]
