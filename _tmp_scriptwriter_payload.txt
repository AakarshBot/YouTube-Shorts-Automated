import html
import json
import os
import re
from html.parser import HTMLParser
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from gnews import GNews

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
MAX_WORDS = 65
MIN_SLIDES = 4
MAX_SLIDES = 5

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
        "status": {"type": "string", "enum": ["ready", "needs_more_sources"]},
        "reason": {"type": "string"},
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
        "titles": {"type": "array", "items": {"type": "string"}},
        "description": {"type": "string"},
        "hashtags": {"type": "array", "items": {"type": "string"}},
        "first_comment": {"type": "string"},
    },
    "required": [
        "status",
        "reason",
        "opening_headline",
        "slides",
        "titles",
        "description",
        "hashtags",
        "first_comment",
    ],
    "additionalProperties": False,
}

SCRIPT_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["ready", "needs_more_sources"]},
        "reason": {"type": "string"},
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
    "required": ["status", "reason", "opening_headline", "slides"],
    "additionalProperties": False,
}

ANGLE_OUTPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["ready", "needs_more_sources"]},
        "reason": {"type": "string"},
        "angles": {
            "type": "array",
            "minItems": 3,
            "maxItems": 3,
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "description": {"type": "string"},
                    "evidence_basis": {"type": "string"},
                },
                "required": ["title", "description", "evidence_basis"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["status", "reason", "angles"],
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


def _clean(value):
    return re.sub(r"\s+", " ", html.unescape(str(value or ""))).strip()


def _valid_url(value):
    parsed = urlparse(str(value or ""))
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def article_text(story):
    if not story or not story.get("url"):
        raise ValueError("Selected story has no source URL.")

    if _valid_url(story["url"]):
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
            text = _clean(" ".join(parser.parts))
            if len(text) >= 300:
                return text[:20000]
        except (HTTPError, URLError, TimeoutError, ValueError):
            pass

    summary = _clean(story.get("description"))
    if summary:
        return f'{_clean(story.get("title"))}. {summary}'
    raise RuntimeError("This source has no readable article text or usable summary.")


def find_related_sources(story):
    news = GNews(language="en", max_results=5, max_retries=1)
    rows = news.get_news(story["title"])
    seen = {story["url"].rstrip("/")}
    sources = []
    for row in rows:
        url = str(row.get("url") or "").strip().rstrip("/")
        title = _clean(row.get("title"))
        if not url or not title or url in seen:
            continue
        try:
            text = article_text({
                "title": title,
                "url": url,
                "description": row.get("description"),
            })
        except (RuntimeError, ValueError):
            continue
        sources.append({
            "title": title,
            "url": url,
            "publisher": _clean(row.get("publisher")),
            "text": text,
        })
        seen.add(url)
    return sources


def manual_sources(urls):
    sources = []
    seen = set()
    for url in urls:
        url = url.strip()
        if not url or url in seen or not _valid_url(url):
            continue
        try:
            text = article_text({"title": url, "url": url})
        except (RuntimeError, ValueError):
            continue
        sources.append({"title": url, "url": url, "publisher": "Manual source", "text": text})
        seen.add(url)
    return sources


def suggest_editorial_angles(story, sources, desk, source_stage="primary", previous=None):
    if not sources:
        raise ValueError("Editorial angles require source evidence.")

    source_text = "\n\n".join(
        f'SOURCE {i}: {item["title"]}\nURL: {item["url"]}\n{item["text"][:12000]}'
        for i, item in enumerate(sources, 1)
    )
    stage_rule = {
        "primary": "Use the primary source first. If it does not contain enough factual material for a substantive Short, return needs_more_sources.",
        "automatic": "Use the primary source plus the automatically found related sources. If the combined evidence is still insufficient, return needs_more_sources.",
        "manual": "Use every usable source provided here, including the manually supplied URLs. If the combined evidence is still insufficient, return needs_more_sources; do not invent or pad the story.",
    }[source_stage]
    previous_text = ""
    if previous:
        previous_text = f"""
Previous script angle:
{previous.get("story_angle", {})}
Previous narration:
{" ".join(slide["voiceover"] for slide in previous.get("slides", []))}

The three new angles must be materially different from the previous story angle and narrative spine.
"""

    prompt = f"""Read the complete research packet for the selected {desk} desk.

Topic Fetcher selection:
{story["title"]}

{source_text}

{stage_rule}
{previous_text}

Your first job is editorial selection, not scriptwriting. Decide whether the evidence is rich enough to build a genuine Short. If it is not, return needs_more_sources with a concise reason and an empty angles array.

When the evidence is enough, return exactly 3 genuinely different, research-backed editorial angles. These are choices for the human editor. They must materially change what the Short is about, not merely rephrase the same summary.

Prefer different evidence-backed lenses such as:
- the event or result itself
- a statement, reaction or key remark when the sources contain a meaningful one
- consequence or why the development matters
- performance, process or how it happened
- an unusual person or detail
- a useful comparison or timeline
- another clearly supported lens that gives the story a distinct editorial spine

Do not force these categories. Use the three strongest choices for this specific story. Do not invent quotes, motives, consequences, criticism, controversy or interpretation that the sources do not support.

For each angle:
- title: 2–5 words, specific to this story, not a generic label such as "Why It Matters" or "Human Angle"
- description: one short sentence explaining what the Short would focus on
- evidence_basis: name the concrete source fact, remark, event, number or detail that makes this angle defensible

The selected angle will become authoritative in the next Scriptwriter step, so each option must be strong enough to support a complete 4–5 slide Short.
"""

    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is not set.")

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": f"You are an experienced editor for the {desk} desk. Source evidence controls factual claims."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.35,
        "max_tokens": 1200,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "editorial_angles",
                "strict": True,
                "schema": ANGLE_OUTPUT_SCHEMA,
            },
        },
    }
    req = Request(
        GROQ_URL,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=45) as response:
            data = json.load(response)
        result = json.loads(data["choices"][0]["message"]["content"])
        errors = validate_editorial_angles(result)
        if errors:
            raise RuntimeError(" · ".join(errors))
        return result
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", "ignore")
        raise RuntimeError(f"Groq request failed: {detail[:500]}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"Groq request failed: {exc}") from exc
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Groq returned an invalid structured response.") from exc


def generate_script(story, sources, desk, previous=None, source_stage="primary", script_only=False, angle=None):
    if not angle:
        raise ValueError("An editorial angle must be selected before writing the Short.")

    source_text = "\n\n".join(
        f'SOURCE {i}: {item["title"]}\nURL: {item["url"]}\n{item["text"][:12000]}'
        for i, item in enumerate(sources, 1)
    )
    previous_text = ""
    if previous:
        previous_text = f"""
Previous draft:
Opening: {previous["opening_headline"]}
Slides: {" ".join(slide["voiceover"] for slide in previous["slides"])}

Build a genuinely different angle and narrative spine. Do not merely swap words or reorder sentences.
"""
    stage_rule = {
        "primary": "Use the primary source first. If it does not contain enough factual material for a substantive Short, return needs_more_sources.",
        "automatic": "Use the primary source plus the automatically found related sources. If the combined evidence is still insufficient, return needs_more_sources.",
        "manual": "Use every usable source provided here, including the manually supplied URLs. If the combined evidence is still insufficient, return needs_more_sources; do not invent or pad the story.",
    }[source_stage]
    redo_instruction = """
This is a script-only redo. Regenerate only the opening screen headline and slide-by-slide voiceover. The previous draft's packaging is intentionally preserved outside the writer. Do not create or change the YouTube titles, description, hashtags or first comment.
""" if script_only else ""

    if isinstance(angle, dict):
        angle_text = (
            f'Angle title: {angle.get("title", "").strip()}\n'
            f'Angle description: {angle.get("description", "").strip()}\n'
            f'Angle evidence basis: {angle.get("evidence_basis", "").strip()}'
        )
    else:
        angle_text = f"Custom editorial angle: {str(angle).strip()}"

    prompt = f"""Create a factual YouTube Short for the selected {desk} desk from the supplied source material.

Topic Fetcher selection:
{story["title"]}

{source_text}
{previous_text}

{stage_rule}

SELECTED EDITORIAL ANGLE — AUTHORITATIVE:
{angle_text}

Build the entire narration around this editorial angle. Do not replace it with the obvious event/result summary. Use the angle to decide what belongs in the Short, how the facts are ordered and what the viewer should understand from the story.

Write from scratch after understanding the full story. The selected Topic Fetcher headline is the starting subject, not the finished script. Do not simply expand, paraphrase or prolong the selected headline.
{redo_instruction}

Story rules:
- Use the available source material as the factual authority.
- You may synthesise information across sources when the sources support the same story.
- Reorder facts however the story needs; do not mechanically follow article paragraphs.
- Capture the important facts, context, names, teams, organisations, events, numbers and remarks needed to understand the story through the selected editorial angle.
- Use exactly 4 or 5 slides. Minimum 4, maximum 5.
- Every slide must add important information. Do not create filler, repetition or artificial sentence splits just to reach 4 or 5 slides.
- Slide 1 spoken narration must contain fewer than 14 words.
- Keep total spoken narration to 65 words or fewer as the proxy for a Short under 30 seconds. The Audio stage may slightly speed the final voice if it is only marginally over 30 seconds.
- Retention must come from real facts, context, contrast, consequence, significance or surprise in the sources.
- Do not invent facts, statistics, quotes, reactions, motives, criticism, controversy, pressure, predictions or consequences.
- If a person is identified in the sources, use their proper name. If the source calls that person a legend, icon, veteran or similar, still name the person when their identity is known. Never hide an identified person's name behind a generic label.
- Preserve the meaning and tone of important remarks.
- If the source does not contain enough of a real story, say so with status needs_more_sources instead of writing a thin or padded Short.

Opening screen headline:
- Exactly 3 or 4 words.
- Specific to the story.

{"""When status is ready, also provide:
- At least two genuinely different YouTube title options.
- One natural description.
- Relevant hashtags only.
- One story-specific first/creator comment that invites a genuine response.
- Packaging must describe the completed Short and introduce no unsupported facts.
""" if not script_only else """For a script-only redo, return only status, reason, opening_headline and slides. Do not generate packaging fields.
"""}When status is needs_more_sources:
- Give a concise reason.
- Return empty script fields; for normal generation also return empty packaging fields.
"""

    key = os.getenv("GROQ_API_KEY")
    if not key:
        raise RuntimeError("GROQ_API_KEY is not set.")

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": f"You are an experienced editor for the {desk} desk. Source evidence controls factual claims."},
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.3,
        "max_tokens": 2400,
        "response_format": {
            "type": "json_schema",
            "json_schema": {
                "name": "script_output" if script_only else "short_output",
                "strict": True,
                "schema": SCRIPT_OUTPUT_SCHEMA if script_only else OUTPUT_SCHEMA,
            },
        },
    }
    req = Request(
        GROQ_URL,
        data=json.dumps(payload).encode(),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
        method="POST",
    )
    try:
        with urlopen(req, timeout=45) as response:
            data = json.load(response)
        result = json.loads(data["choices"][0]["message"]["content"])
        if result.get("status") == "ready":
            result["story_angle"] = angle
        return result
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", "ignore")
        raise RuntimeError(f"Groq request failed: {detail[:500]}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError(f"Groq request failed: {exc}") from exc
    except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
        raise RuntimeError("Groq returned an invalid structured response.") from exc


def validate_editorial_angles(result):
    if not isinstance(result, dict):
        return ["Editorial angle output is not an object."]

    status = result.get("status")
    if status == "needs_more_sources":
        return [] if str(result.get("reason", "")).strip() else ["A reason is required when more sources are needed."]
    if status != "ready":
        return ["Editorial angle status must be ready or needs_more_sources."]

    angles = result.get("angles")
    if not isinstance(angles, list) or len(angles) != 3:
        return ["Exactly three editorial angles are required."]

    errors = []
    titles = []
    for index, angle in enumerate(angles, 1):
        if not isinstance(angle, dict):
            errors.append(f"Editorial angle {index} is invalid.")
            continue
        title = str(angle.get("title", "")).strip()
        description = str(angle.get("description", "")).strip()
        evidence = str(angle.get("evidence_basis", "")).strip()
        if not title or not description or not evidence:
            errors.append(f"Editorial angle {index} must include a title, description and evidence basis.")
        if not 2 <= len(re.findall(r"\b\S+\b", title)) <= 5:
            errors.append(f"Editorial angle {index} title must contain 2–5 words.")
        titles.append(re.sub(r"\s+", " ", title.lower()))
    if len(set(titles)) != len(titles):
        errors.append("Editorial angle titles must be unique.")
    return errors


def validate_script(result):
    if not isinstance(result, dict):
        return ["Script output is not an object."]

    status = result.get("status")
    if status == "needs_more_sources":
        return [] if str(result.get("reason", "")).strip() else ["A reason is required when more sources are needed."]
    if status != "ready":
        return ["Script status must be ready or needs_more_sources."]

    headline = str(result.get("opening_headline", "")).strip()
    slides = result.get("slides", [])
    errors = []
    if not slides or not all(isinstance(slide, dict) for slide in slides):
        errors.append("Every slide must be an object.")
    elif not MIN_SLIDES <= len(slides) <= MAX_SLIDES:
        errors.append(f"Script must contain {MIN_SLIDES}–{MAX_SLIDES} slides.")
    elif len(re.findall(r"\b\w+[’'-]?\w*\b", slides[0].get("voiceover", ""))) >= 14:
        errors.append("Slide 1 must contain fewer than 14 words.")

    words = sum(
        len(re.findall(r"\b\w+[’'-]?\w*\b", slide.get("voiceover", "")))
        for slide in slides
        if isinstance(slide, dict)
    )
    if words > MAX_WORDS:
        errors.append("Total narration must be 65 words or fewer.")
    if not all(isinstance(slide, dict) and slide.get("voiceover", "").strip() for slide in slides):
        errors.append("Every slide needs spoken narration.")
    if len(re.findall(r"\b\S+\b", headline)) not in (3, 4):
        errors.append("Opening headline must contain exactly 3 or 4 words.")
    if not result.get("story_angle"):
        errors.append("A selected editorial angle is required.")
    voices = [slide["voiceover"].strip().lower() for slide in slides if isinstance(slide, dict) and slide.get("voiceover")]
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
