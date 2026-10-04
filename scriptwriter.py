import html
import json
import os
import re
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")

if not os.getenv("GROQ_API_KEY"):
    path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.isfile(path):
        with open(path, encoding="utf-8-sig") as env_file:
            for line in env_file:
                name, separator, value = line.strip().partition("=")
                if separator and name.strip().removeprefix("export ").strip() == "GROQ_API_KEY":
                    os.environ["GROQ_API_KEY"] = value.strip().strip("'").strip('"')
                    break

OUTPUT_SCHEMA = {
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
        "titles": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 2,
        },
        "description": {"type": "string"},
        "hashtags": {
            "type": "array",
            "items": {"type": "string"},
            "minItems": 1,
        },
        "first_comment": {"type": "string"},
    },
    "required": [
        "opening_headline",
        "slides",
        "titles",
        "description",
        "hashtags",
        "first_comment",
    ],
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
        req = Request(story["url"], headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=12) as response:
            raw = response.read(300000).decode("utf-8", "ignore")
        article = re.search(r"<article\b.*?</article>", raw, flags=re.I | re.S)
        parser = _Text()
        parser.feed(
            re.sub(
                r"<head.*?</head>",
                " ",
                article.group(0) if article else raw,
                flags=re.I | re.S,
            )
        )
        text = re.sub(r"\s+", " ", html.unescape(" ".join(parser.parts))).strip()
        if len(text) >= 300:
            return text[:20000]
    except (HTTPError, URLError, TimeoutError, ValueError):
        pass

    summary = re.sub(
        r"\s+", " ", html.unescape(str(story.get("description") or ""))
    ).strip()
    if summary:
        return f'{story["title"]}. {summary}'
    raise RuntimeError("The selected story has no readable source evidence.")


def generate_script(story, source, previous=None):
    previous_text = ""
    if previous:
        previous_text = f"""
Previous draft:
Opening: {previous["opening_headline"]}
Slides: {" ".join(slide["voiceover"] for slide in previous["slides"])}

Create a genuinely different editorial angle and narrative spine. Do not merely swap words.
"""
    prompt = f"""Create a factual YouTube Short from this source.

Selected Topic Fetcher headline:
{story["title"]}

Source evidence:
{source[:18000]}
{previous_text}

Work in this order:
1. Understand the source and decide what actually happened.
2. Choose the strongest supported editorial angle.
3. Write the complete 4-slide Short, using 5 only when necessary.
4. Only after the story is complete, create the YouTube titles, description, hashtags and first comment to package that finished Short.

The selected Topic Fetcher headline is context only. There is no approved YouTube title and no title should influence the story.

Story rules:
- Write from the source evidence, not from the headline alone.
- Reorder and synthesise facts; do not follow source paragraphs mechanically.
- Cover the important facts and context. Four slides should normally cover roughly 90% of the important story.
- Slide 1 spoken narration must contain fewer than 14 words.
- Total narration must fit 30 seconds and stay at or below 75 words.
- Every slide must add important information.
- Name central people, teams, organisations, events and other specific entities explicitly.
- If a named person is central, use their actual name. Never replace them with "a legend", "a star", "the veteran" or "the player".
- If a person's remark or opinion is central, identify that person and preserve the meaning and tone of the remark.
- Do not let the selected headline determine the story angle.
- Do not turn praise into criticism, advice into a demand, possibility into certainty or one detail into a larger narrative without evidence.
- Do not invent controversy, criticism, pressure, doubts about form, legacy concerns, retirement implications, motives, reactions, stakes or consequences.
- Do not invent facts, statistics, quotes, predictions or conclusions.
- Retention must come from actual facts, context, contrast, consequence, significance or surprise in the source.
- No filler, repetition, generic AI-news language or clickbait.
- Opening screen headline must be exactly 3 or 4 words and specifically identify the story.

Packaging rules:
- Titles must accurately represent the completed Short.
- Generate at least two genuinely different title angles.
- Put important names and story terms early.
- Description must explain the actual story naturally.
- Hashtags must be relevant only.
- The first comment must be specific to this story and invite a genuine response.
- Do not let packaging introduce facts that are absent from the source or completed Short.
"""
    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is not set.")

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "system",
                "content": "You are an experienced sports/news editor. The supplied source is the factual authority.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 2400,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "short_output",
                "strict": True,
                "schema": OUTPUT_SCHEMA,
            },
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
            return json.loads(json.load(response)["choices"][0]["message"]["content"])
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", "ignore")
        raise RuntimeError(f"Groq request failed: {detail[:500]}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"Groq request failed: {exc}") from exc
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Groq returned an invalid structured response.") from exc


def validate_script(result):
    if not isinstance(result, dict):
        return ["Script output is not an object."]

    headline = str(result.get("opening_headline", "")).strip()
    slides = result.get("slides", [])
    errors = []

    if len(slides) not in (4, 5):
        errors.append("Script must contain 4 or 5 slides.")
    if not slides or not all(isinstance(slide, dict) for slide in slides):
        errors.append("Every slide must be an object.")
    elif len(re.findall(r"\b\w+[’'-]?\w*\b", slides[0].get("voiceover", ""))) >= 14:
        errors.append("Slide 1 must contain fewer than 14 words.")

    words = sum(
        len(re.findall(r"\b\w+[’'-]?\w*\b", slide.get("voiceover", "")))
        for slide in slides
        if isinstance(slide, dict)
    )
    if words > 75:
        errors.append("Total narration is too long for the 30-second target.")
    if not all(
        isinstance(slide, dict) and slide.get("voiceover", "").strip()
        for slide in slides
    ):
        errors.append("Every slide needs spoken narration.")
    if len(re.findall(r"\b\S+\b", headline)) not in (3, 4):
        errors.append("Opening headline must contain exactly 3 or 4 words.")

    voices = [
        slide["voiceover"].strip().lower()
        for slide in slides
        if isinstance(slide, dict) and slide.get("voiceover")
    ]
    if len(set(voices)) < len(voices):
        errors.append("Slides must not be duplicated.")

    if len(result.get("titles", [])) < 2:
        errors.append("At least two title options are required.")
    if not str(result.get("description", "")).strip():
        errors.append("Description is required.")
    if not result.get("hashtags"):
        errors.append("At least one relevant hashtag is required.")
    if not str(result.get("first_comment", "")).strip():
        errors.append("First comment is required.")
    return errors
