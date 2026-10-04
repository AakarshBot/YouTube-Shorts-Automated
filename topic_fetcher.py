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
    r'"records? & stats"|"team records"|"career stats"|\bcricket grounds\b',
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
    return _clean(value).split("?")[0].rstrip("/").lower()

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
            max_results=40 if blocked_urls else 20,
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
