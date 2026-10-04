import json

from scriptwriter import MAX_SLIDES, MAX_WORDS, MIN_SLIDES, validate_script


def make_ready(slides=None, headline="Rohit Sharma Praise"):
    return {
        "status": "ready",
        "reason": "",
        "opening_headline": headline,
        "slides": slides or [
            {"voiceover": "Rohit Sharma got praise."},
            {"voiceover": "The former captain explained why his experience matters."},
            {"voiceover": "The point centred on India's batting during pressure."},
            {"voiceover": "His experience remains central to India's decision-making."},
        ],
        "titles": ["Rohit Sharma Praise", "Why Rohit's Experience Matters"],
        "description": "The key point about Rohit Sharma's role.",
        "hashtags": ["#RohitSharma", "#Cricket"],
        "first_comment": "Do you agree with the assessment?",
    }


def test_valid_ready_output():
    assert validate_script(make_ready()) == []


def test_slide_count_must_be_four_or_five():
    assert validate_script(make_ready(slides=[{"voiceover": f"Important fact {i}"} for i in range(3)]))[0] == f"Script must contain {MIN_SLIDES}–{MAX_SLIDES} slides."
    assert validate_script(make_ready(slides=[{"voiceover": f"Important fact {i}"} for i in range(4)])) == []
    assert validate_script(make_ready(slides=[{"voiceover": f"Important fact {i}"} for i in range(5)])) == []
    assert validate_script(make_ready(slides=[{"voiceover": f"Important fact {i}"} for i in range(6)]))[0] == f"Script must contain {MIN_SLIDES}–{MAX_SLIDES} slides."

def test_first_slide_must_be_under_fourteen_words():
    result = make_ready(slides=[
        {"voiceover": "One two three four five six seven eight nine ten eleven twelve thirteen fourteen"},
        {"voiceover": "Second fact."},
        {"voiceover": "Third fact."},
        {"voiceover": "Fourth fact."},
    ])
    assert "Slide 1 must contain fewer than 14 words." in validate_script(result)


def test_total_narration_must_be_65_words_or_less():
    long = " ".join(["word"] * (MAX_WORDS + 1))
    result = make_ready(slides=[{"voiceover": long}])
    assert "Total narration must be 65 words or fewer." in validate_script(result)


def test_needs_more_sources_is_valid_without_script_fields():
    result = {
        "status": "needs_more_sources",
        "reason": "The primary source only reports the claim and gives no supporting detail.",
        "opening_headline": "",
        "slides": [],
        "titles": [],
        "description": "",
        "hashtags": [],
        "first_comment": "",
    }
    assert validate_script(result) == []


def test_duplicate_slides_are_rejected():
    result = make_ready(slides=[{"voiceover": "Same line."}] * 4)
    assert "Slides must not be duplicated." in validate_script(result)


def test_packaging_is_required():
    result = make_ready()
    result["titles"] = []
    result["description"] = ""
    result["hashtags"] = []
    result["first_comment"] = ""
    errors = validate_script(result)
    assert "At least two title options are required." in errors
    assert "Description is required." in errors
    assert "At least one relevant hashtag is required." in errors
    assert "First comment is required." in errors


class _Response:
    def __init__(self, body):
        self.body = body.encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size=-1):
        return self.body


def test_source_article_is_used_when_reachable(monkeypatch):
    import scriptwriter

    def fake_urlopen(req, timeout=12):
        return _Response("<html><article>" + ("Important article fact. " * 30) + "</article></html>")

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    text = scriptwriter.article_text({
        "title": "Story",
        "url": "https://example.com/story",
        "description": "Short summary.",
    })
    assert text.startswith("Important article fact.")


def test_gnews_summary_is_used_as_fallback(monkeypatch):
    import scriptwriter
    from urllib.error import HTTPError

    def fake_urlopen(req, timeout=12):
        raise HTTPError(req.full_url, 400, "Bad Request", {}, None)

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    text = scriptwriter.article_text({
        "title": "Story headline",
        "url": "https://example.com/story",
        "description": "GNews summary.",
    })
    assert text == "Story headline. GNews summary."


def test_invalid_source_url_uses_summary_without_request(monkeypatch):
    import scriptwriter

    def fake_urlopen(req, timeout=12):
        raise AssertionError("Invalid URL should not be opened")

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    text = scriptwriter.article_text({
        "title": "Story headline",
        "url": "not-a-url",
        "description": "GNews summary.",
    })
    assert text == "Story headline. GNews summary."


def test_related_sources_use_existing_gnews(monkeypatch):
    import scriptwriter

    class FakeGNews:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def get_news(self, title):
            return [{
                "title": "Related report",
                "url": "https://example.com/related",
                "publisher": "Example",
                "description": "Related detail.",
            }]

    monkeypatch.setattr(scriptwriter, "GNews", FakeGNews)
    monkeypatch.setattr(scriptwriter, "article_text", lambda story: "A" * 400)
    result = scriptwriter.find_related_sources({
        "title": "Story",
        "url": "https://example.com/story",
    })
    assert result[0]["url"] == "https://example.com/related"


def test_generation_prompt_contains_locked_story_rules(monkeypatch):
    import scriptwriter

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    captured = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, size=-1):
            return b'{"choices":[{"message":{"content":"{\\"status\\":\\"ready\\",\\"reason\\":\\"\\",\\"opening_headline\\":\\"Rohit Gets Praise\\",\\"slides\\":[{\\"voiceover\\":\\"Rohit Sharma got praise.\\"},{\\"voiceover\\":\\"His experience was the key reason.\\"}],\\"titles\\":[\\"Rohit Sharma Gets Praise\\",\\"Why Rohit\\"],\\"description\\":\\"The story.\\",\\"hashtags\\":[\\"#Cricket\\"],\\"first_comment\\":\\"Thoughts?\\"}"}}]}'

    def fake_urlopen(req, timeout=45):
        captured["body"] = json.loads(req.data)
        return Response()

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    scriptwriter.generate_script(
        {"title": "Indian legend praises Rohit Sharma"},
        [{"title": "Source", "url": "https://example.com", "text": "A named source identifies Sunil Gavaskar."}],
        "Cricket — India / Pakistan / Sri Lanka / Asia",
    )
    prompt = captured["body"]["messages"][1]["content"]
    assert "Write from scratch after understanding the full story." in prompt
    assert "Use exactly 4 or 5 slides." in prompt
    assert "There is no fixed slide count." not in prompt
    assert "65 words or fewer" in prompt
    assert "use their proper name" in prompt
    assert "Approved YouTube title" not in prompt
    assert "Cricket — India / Pakistan / Sri Lanka / Asia" in captured["body"]["messages"][0]["content"]


def test_script_only_redo_preserves_packaging(monkeypatch):
    import scriptwriter

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    previous = make_ready(
        slides=[
            {"voiceover": "Original opening."},
            {"voiceover": "Original second fact."},
            {"voiceover": "Original third fact."},
            {"voiceover": "Original ending."},
        ],
        headline="Original Script",
    )
    generated = make_ready(
        slides=[
            {"voiceover": "New opening."},
            {"voiceover": "New second fact."},
            {"voiceover": "New third fact."},
            {"voiceover": "New ending."},
        ],
        headline="New Script",
    )
    generated["titles"] = ["Changed title", "Another changed title"]
    generated["description"] = "Changed description."
    generated["hashtags"] = ["#Changed"]
    generated["first_comment"] = "Changed comment."

    body = json.dumps({
        "choices": [{
            "message": {
                "content": json.dumps(generated),
            }
        }]
    })

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, size=-1):
            return body.encode()

    monkeypatch.setattr(scriptwriter, "urlopen", lambda req, timeout=45: Response())

    result = scriptwriter.generate_script(
        {"title": "Story"},
        [{"title": "Source", "url": "https://example.com", "text": "Important source facts."}],
        "Cricket — India / Pakistan / Sri Lanka / Asia",
        previous=previous,
        script_only=True,
    )

    assert result["opening_headline"] == generated["opening_headline"]
    assert result["slides"] == generated["slides"]
    assert result["titles"] == previous["titles"]
    assert result["description"] == previous["description"]
    assert result["hashtags"] == previous["hashtags"]
    assert result["first_comment"] == previous["first_comment"]
