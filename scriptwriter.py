import html
import json
import os
import re
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
HEADLINE_SCHEMA = {
    "type": "object",
    "properties": {"titles": {"type": "array", "items": {"type": "string"}}},
    "required": ["titles"],
    "additionalProperties": False,
}
SCRIPT_SCHEMA = {
    "type": "object",
    "properties": {
        "opening_headline": {"type": "string"},
        "slides": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"voiceover": {"type": "string"}},
                "required": ["voiceover"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["opening_headline", "slides"],
    "additionalProperties": False,
}


class _Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag.lower() in {"script", "style", "noscript", "svg"}:
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def article_text(story):
    if not story or not story.get("url"):
        raise ValueError("Selected story has no source URL.")

    try:
        req = Request(
            story["url"],
            headers={
                "User-Agent": "Mozilla/5.0",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
            },
        )
        with urlopen(req, timeout=12) as response:
            raw = response.read(300000).decode("utf-8", "ignore")
        article = re.search(r"<article\b[\s\S]*?</article>", raw, flags=re.I)
        target = article.group(0) if article else raw
        parser = _Text()
        parser.feed(re.sub(r"<head[\s\S]*?</head>", " ", target, flags=re.I))
        text = re.sub(r"\s+", " ", html.unescape(" ".join(parser.parts))).strip()
        if len(text) >= 300:
            return text[:20000]
    except (HTTPError, URLError, TimeoutError, ValueError):
        pass

    summary = re.sub(r"\s+", " ", html.unescape(str(story.get("description") or ""))).strip()
    if summary:
        return f'{story["title"]}. {summary}'
    raise RuntimeError("The selected story has no readable source evidence.")


def _groq(schema_name, schema, system, user):
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is not set.")
    payload = {
        "model": MODEL,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "temperature": 0.4,
        "max_tokens": 1800,
        "response_format": {
            "type": "json_schema",
            "json_schema": {"name": schema_name, "strict": True, "schema": schema},
        },
    }
    req = Request(
        GROQ_URL,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=45) as response:
            data = json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", "ignore")
        raise RuntimeError(f"Groq request failed: {detail[:500]}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"Groq request failed: {exc}") from exc
    try:
        return json.loads(data["choices"][0]["message"]["content"])
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Groq returned an invalid structured response.") from exc


def generate_titles(story, source):
    title = story["title"]
    prompt = f"""Write YouTube Shorts title options for this story.

Selected headline:
{title}

Source:
{source[:12000]}

Return as many strong options as the story genuinely supports. There is no required count.
Use meaningfully different packaging angles, such as direct/result-led, consequence/significance-led, or intrigue-led when supported.
Keep every option accurate to the source, concise, natural, Shorts-friendly, with important words early.
No clickbait, fake curiosity, unsupported claims, excessive capitals or emoji.
Do not simply rewrite the supplied headline."""
    titles = _groq(
        "short_titles",
        HEADLINE_SCHEMA,
        "You are a sharp sports/news video editor. Facts in the supplied source are the only authority.",
        prompt,
    )["titles"]
    if not titles:
        raise RuntimeError("No title options were returned.")
    return titles


def generate_script(story, approved_title, source, improve=False):
    angle = (
        "Create a genuinely different editorial angle and narrative spine from the previous draft. "
        "Do not merely swap words."
        if improve
        else "Choose the strongest supported editorial angle for the first draft."
    )
    prompt = f"""Write the spoken script and opening screen headline for a YouTube Short.

Selected source headline:
{story["title"]}

Approved YouTube title:
{approved_title}

Source evidence:
{source[:18000]}

{angle}

Rules:
- 4 or 5 slides; use 4 unless a fifth contains necessary information.
- Slide 1 spoken narration must be fewer than 14 words.
- Total spoken narration must fit 30 seconds at normal delivery; do not stretch the story.
- Every slide must add important information.
- The source is evidence, not the script. Write from scratch, reorder facts and synthesise the strongest details.
- Cover roughly 90% of the important source information across four slides unless a fifth is genuinely necessary.
- Build retention through real facts, tension, consequence, significance or surprise. Never withhold the answer or use fake curiosity.
- No invented facts, motives, quotes, numbers, reactions or predictions.
- No filler, repetition, generic AI-news language, forced jokes or clickbait.
- Keep the voice confident, sharp, human and natural for spoken delivery.
- Opening headline must be exactly 3 or 4 words, story-specific and contain zero filler."""
    return _groq(
        "short_script",
        SCRIPT_SCHEMA,
        "You are an experienced editor writing concise, factual YouTube Shorts scripts.",
        prompt,
    )


def validate_script(script, approved_title):
    if not approved_title.strip():
        return ["Approved title is missing."]
    headline = str(script.get("opening_headline", "")).strip()
    slides = script.get("slides", [])
    errors = []
    if len(slides) not in (4, 5):
        errors.append("Script must contain 4 or 5 slides.")
    if len(re.findall(r"\b\w+[’'-]?\w*\b", slides[0]["voiceover"])) >= 14 if slides else True:
        errors.append("Slide 1 must contain fewer than 14 words.")
    words = sum(len(re.findall(r"\b\w+[’'-]?\w*\b", s.get("voiceover", ""))) for s in slides)
    if words > 75:
        errors.append("Total narration is too long for the 30-second target.")
    if any(not s.get("voiceover", "").strip() for s in slides):
        errors.append("Every slide needs spoken narration.")
    if len(re.findall(r"\b\S+\b", headline)) not in (3, 4):
        errors.append("Opening headline must contain exactly 3 or 4 words.")
    if len({s["voiceover"].strip().lower() for s in slides if s.get("voiceover")}) < len(slides):
        errors.append("Slides must not be duplicated.")
    return errors
