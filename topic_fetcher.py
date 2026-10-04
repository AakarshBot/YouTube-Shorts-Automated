from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
import re

from gnews import GNews

GENRES = {
    "Cricket — India / Pakistan / Sri Lanka / Asia": {
        "India": [(
            "IN",
            '("India cricket" OR BCCI OR Kohli OR Rohit OR Gill OR Bumrah OR Pant OR Rahul OR Jadeja OR Jaiswal OR "India T20" OR "India ODI" OR "India Test") when:1d '
            '-"records & stats" -"team records" -"career stats" -scorecard -fixtures -fixture -schedule -rankings -archive -gallery -quiz -odds -"cricket grounds"'
        )],
        "Pakistan": [(
            "PK",
            '("Pakistan cricket" OR PCB OR Babar OR Shaheen OR Rizwan OR Naseem OR "Pakistan T20" OR "Pakistan ODI" OR "Pakistan Test") when:1d '
            '-"records & stats" -"team records" -"career stats" -scorecard -fixtures -fixture -schedule -rankings -archive -gallery -quiz -odds -"cricket grounds"'
        )],
        "Sri Lanka": [(
            "LK",
            '("Sri Lanka cricket" OR SLC OR Hasaranga OR Mendis OR Nissanka OR Mathews OR "Sri Lanka T20" OR "Sri Lanka ODI" OR "Sri Lanka Test") when:1d '
            '-"records & stats" -"team records" -"career stats" -scorecard -fixtures -fixture -schedule -rankings -archive -gallery -quiz -odds -"cricket grounds"'
        )],
        "Bangladesh": [(
            "BD",
            '("Bangladesh cricket" OR BCB OR Shanto OR Mushfiqur OR Mahmudullah OR "Bangladesh T20" OR "Bangladesh ODI" OR "Bangladesh Test") when:1d '
            '-"records & stats" -"team records" -"career stats" -scorecard -fixtures -fixture -schedule -rankings -archive -gallery -quiz -odds -"cricket grounds"'
        )],
        "Afghanistan": [(
            "AF",
            '("Afghanistan cricket" OR ACB OR Rashid OR Nabi OR Gurbaz OR "Afghanistan T20" OR "Afghanistan ODI" OR "Afghanistan Test") when:1d '
            '-"records & stats" -"team records" -"career stats" -scorecard -fixtures -fixture -schedule -rankings -archive -gallery -quiz -odds -"cricket grounds"'
        )],
    },
    "Cricket — Global": {
        "Australia": [(
            "AU",
            '("Australia cricket" OR Cricket Australia OR Cummins OR Smith OR Starc OR Head OR "Australia T20" OR "Australia ODI" OR "Australia Test") when:1d '
            '-"records & stats" -"team records" -"career stats" -scorecard -fixtures -fixture -schedule -rankings -archive -gallery -quiz -odds -"cricket grounds"'
        )],
        "England": [(
            "GB",
            '("England cricket" OR ECB OR Stokes OR Root OR Brook OR Buttler OR "England T20" OR "England ODI" OR "England Test") when:1d '
            '-"records & stats" -"team records" -"career stats" -scorecard -fixtures -fixture -schedule -rankings -archive -gallery -quiz -odds -"cricket grounds"'
        )],
        "South Africa": [(
            "ZA",
            '("South Africa cricket" OR CSA OR Bavuma OR Rabada OR Markram OR de Kock OR "South Africa T20" OR "South Africa ODI" OR "South Africa Test") when:1d '
            '-"records & stats" -"team records" -"career stats" -scorecard -fixtures -fixture -schedule -rankings -archive -gallery -quiz -odds -"cricket grounds"'
        )],
        "New Zealand": [(
            "NZ",
            '("New Zealand cricket" OR NZC OR Williamson OR Mitchell OR Conway OR Southee OR "New Zealand T20" OR "New Zealand ODI" OR "New Zealand Test") when:1d '
            '-"records & stats" -"team records" -"career stats" -scorecard -fixtures -fixture -schedule -rankings -archive -gallery -quiz -odds -"cricket grounds"'
        )],
        "Ireland": [(
            "IE",
            '("Ireland cricket" OR Cricket Ireland OR Balbirnie OR Stirling OR "Ireland T20" OR "Ireland ODI" OR "Ireland Test") when:1d '
            '-"records & stats" -"team records" -"career stats" -scorecard -fixtures -fixture -schedule -rankings -archive -gallery -quiz -odds -"cricket grounds"'
        )],
        "Zimbabwe": [(
            "ZW",
            '("Zimbabwe cricket" OR Zimbabwe Cricket OR Raza OR Ervine OR Williams OR "Zimbabwe T20" OR "Zimbabwe ODI" OR "Zimbabwe Test") when:1d '
            '-"records & stats" -"team records" -"career stats" -scorecard -fixtures -fixture -schedule -rankings -archive -gallery -quiz -odds -"cricket grounds"'
        )],
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

DESK_PILLS = {
    "News": {
        "India": [("IN", "India national news major developments when:1d")],
        "World": [("US", "world international major developments when:1d")],
        "Politics & Policy": [("IN", "India government parliament policy election court when:1d")],
        "Major Events": [("IN", "India world conflict disaster major event when:1d")],
    },
    "Entertainment": {
        "Indian Film & OTT": [("IN", "Bollywood Indian cinema OTT streaming when:1d")],
        "Global Film & TV": [("US", "Hollywood film TV streaming when:1d")],
        "Music": [("US", "music artist singer album tour when:1d")],
        "Celebrities": [("US", "celebrity actor actress statement award when:1d")],
    },
    "Technology": {
        "AI": [("US", "artificial intelligence AI OpenAI Google Microsoft when:1d")],
        "Phones & Gadgets": [("US", "smartphone gadget device launch when:1d")],
        "Big Tech & Platforms": [("US", "Google Apple Microsoft Meta Amazon technology when:1d")],
        "Startups & Innovation": [("IN", "India tech startup funding innovation when:1d")],
    },
    "Business & Finance": {
        "India Markets": [("IN", "India stock market Sensex Nifty shares when:1d")],
        "Global Markets": [("US", "global markets stocks economy when:1d")],
        "Companies & Deals": [("US", "companies merger acquisition deal earnings when:1d")],
        "Economy & Policy": [("IN", "India economy RBI inflation policy trade when:1d")],
    },
    "Gaming": {
        "Games & Releases": [("US", "video game game release update when:1d")],
        "Esports": [("US", "esports tournament team player when:1d")],
        "Industry & Platforms": [("US", "gaming industry publisher developer platform when:1d")],
        "Hardware": [("US", "gaming console PC hardware GPU when:1d")],
    },
    "Science & Space": {
        "Space": [("US", "space NASA mission satellite rocket when:1d")],
        "Science & Research": [("US", "science research breakthrough discovery when:1d")],
        "Environment & Climate": [("US", "climate environment nature major study when:1d")],
        "Major Discoveries": [("US", "scientific discovery new species physics astronomy when:1d")],
    },
}

DESKS = {
    "Sports": tuple(GENRES),
    "News": tuple(DESK_PILLS["News"]),
    "Entertainment": tuple(DESK_PILLS["Entertainment"]),
    "Technology": tuple(DESK_PILLS["Technology"]),
    "Business & Finance": tuple(DESK_PILLS["Business & Finance"]),
    "Gaming": tuple(DESK_PILLS["Gaming"]),
    "Science & Space": tuple(DESK_PILLS["Science & Space"]),
}

BAD = re.compile(
    r"\b(schedule|fixtures?|standings?|scorecard|live score|how to watch|where to watch|"
    r"predicted xi|predicted lineups?|photo gallery|photos?|quiz|odds|recap|round[- ]up|"
    r"tournament review|what we learned|live updates?|live blog|horoscope)\b|"
    r"\brecords? & stats\b|\bteam records\b|\bcareer stats\b|\bcricket grounds\b",
    re.I,
)

CRICKET_ONLY = re.compile(
    r"\b(cricket|cricketer|wicket|innings?|batter|batsman|batsmen|bowler|bowling|batting|"
    r"stumps?|lbw|bcci|pcb|slc|icc|psl|ipl|wpl|bbl|cpl|odi|t20|test match|one-day)\b",
    re.I,
)

def _clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()

def _url(value):
    return _clean(value).rstrip("/").lower()

def _group_india_rows(rows, limit=25):
    single_stop = {
        "after", "all", "amid", "and", "are", "before", "beat", "beats", "beating",
        "cricket", "cup", "day", "for", "from", "game", "games", "has", "have", "india",
        "in", "into", "is", "latest", "league", "live", "match", "matches", "new", "news",
        "odi", "one", "on", "or", "over", "player", "players", "report", "reports", "said",
        "say", "says", "score", "scores", "series", "set", "star", "stars", "team", "teams",
        "test", "the", "this", "t20", "to", "today", "tomorrow", "tournament", "trophy",
        "two", "update", "updates", "vs", "with", "win", "wins", "won", "world", "yesterday"
    }
    bad_phrases = {"india cricket", "cricket match", "india team", "india player", "cricket news"}
    token_re = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)?")
    counts, display, per_row = {}, {}, []

    for row in rows:
        title = re.sub(r"['’]s\b", "", row["title"], flags=re.I)
        original = token_re.findall(title)
        tokens = [token.lower() for token in original]
        seen = set()
        for size in (3, 2, 1):
            for i in range(len(tokens) - size + 1):
                key = " ".join(tokens[i:i + size])
                if any(len(word) < 3 for word in key.split()):
                    continue
                if size == 1 and key in single_stop:
                    continue
                if size > 1 and key in bad_phrases:
                    continue
                seen.add(key)
                display.setdefault(key, " ".join(original[i:i + size]))
        per_row.append(seen)
        for key in seen:
            counts[key] = counts.get(key, 0) + 1

    groups = {}
    for row, candidates in zip(rows, per_row):
        repeated = [key for key in candidates if counts[key] > 1]
        candidates = repeated or [key for key in candidates if len(key.split()) <= 2] or list(candidates)
        key = max(candidates, key=lambda value: (len(value.split()), counts[value], len(value)))
        groups.setdefault(key, {"topic": display[key], "headlines": []})["headlines"].append(row)

    ordered = sorted(groups.values(), key=lambda group: group["headlines"][0]["published_at"], reverse=True)
    for group in ordered:
        group["headlines"] = [
            {
                **row,
                "published_at": row["published_at"].isoformat()
                if isinstance(row["published_at"], datetime) else row["published_at"],
            }
            for row in group["headlines"]
        ]
    return ordered[:limit]

def fetch_topics(genre, exclude_urls=()):
    if genre not in GENRES and genre not in DESK_PILLS:
        raise ValueError(f"Unknown genre: {genre}")

    blocked_urls = {_url(x) for x in exclude_urls}
    source_map = GENRES if genre in GENRES else DESK_PILLS
    searches = [
        (label, country, query)
        for label, sources in source_map[genre].items()
        for country, query in sources
    ]

    def fetch(search):
        label, country, query = search
        news = GNews(
            language="en",
            country=country,
            max_results=100 if genre == "Cricket — India / Pakistan / Sri Lanka / Asia" and label == "India" and not blocked_urls else 20 if not blocked_urls else 40,
            max_retries=1,
        )
        return label, news.get_news(query)

    with ThreadPoolExecutor(max_workers=min(8, len(searches))) as pool:
        grouped = {label: [] for label in source_map[genre]}
        seen = set(blocked_urls)
        for label, batch in pool.map(fetch, searches):
            for item in batch:
                title, url = _clean(item.get("title")), _url(item.get("url"))
                if not title or not url or url in seen or BAD.search(title):
                    continue
                if genre.startswith("Cricket") and not CRICKET_ONLY.search(title):
                    continue
                if genre == "Niche Sports — Global" and CRICKET_ONLY.search(title):
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

        if genre == "Cricket — India / Pakistan / Sri Lanka / Asia" and label == "India":
            groups = _group_india_rows(fresh)
            if len(groups) < 25:
                groups = _group_india_rows([
                    r for r in rows if r["published_at"] >= now - timedelta(hours=72)
                ])
            if groups:
                headlines = [h for group in groups for h in group["headlines"]]
                result.append({
                    "topic": label,
                    "groups": groups,
                    "headlines": [
                        {
                            "title": r["title"],
                            "url": r["url"],
                            "publisher": r["publisher"],
                            "published_at": r["published_at"],
                        }
                        for r in headlines
                    ],
                })
            continue

        if genre == "Cricket — India / Pakistan / Sri Lanka / Asia":
            rows = fresh if len(fresh) >= 5 else [
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
