import json

from scriptwriter import validate_script


def make_output(headline="Rohit Sharma Gets Praise", slides=None):
    return {
        "opening_headline": headline,
        "slides": slides or [
            {"voiceover": "Rohit Sharma got praise."},
            {"voiceover": "The legend explained why."},
            {"voiceover": "His comments focused on centuries."},
            {"voiceover": "That is the key detail from the story."},
        ],
        "titles": ["Rohit Sharma Gets Praise", "Legend Praises Rohit Sharma"],
        "description": "A legend praised Rohit Sharma.",
        "hashtags": ["#RohitSharma", "#Cricket"],
        "first_comment": "Was this the right praise for Rohit?",
    }


def test_valid_four_slide_output():
    assert validate_script(make_output()) == []


def test_valid_five_slide_output():
    script = make_output(
        slides=[{"voiceover": f"Important fact {i}"} for i in range(5)]
    )
    assert validate_script(script) == []


def test_first_slide_must_be_under_fourteen_words():
    script = make_output(
        slides=[
            {"voiceover": "One two three four five six seven eight nine ten eleven twelve thirteen fourteen"},
            {"voiceover": "Second fact"},
            {"voiceover": "Third fact"},
            {"voiceover": "Fourth fact"},
        ]
    )
    assert "Slide 1 must contain fewer than 14 words." in validate_script(script)


def test_opening_headline_must_be_three_or_four_words():
    assert "Opening headline must contain exactly 3 or 4 words." in validate_script(
        make_output("Two Words")
    )


def test_narration_must_fit_thirty_second_target():
    long = " ".join(["word"] * 76)
    result = make_output(slides=[{"voiceover": long}] * 4)
    assert "Total narration is too long for the 30-second target." in validate_script(result)


def test_duplicate_slides_are_rejected():
    result = make_output(slides=[{"voiceover": "Same line"}] * 4)
    assert "Slides must not be duplicated." in validate_script(result)


def test_packaging_is_required():
    result = make_output()
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


def test_gnews_summary_is_used_when_source_returns_400(monkeypatch):
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


def test_source_without_article_element_can_still_be_used(monkeypatch):
    import scriptwriter

    def fake_urlopen(req, timeout=12):
        return _Response("<html><body>" + ("Important article fact. " * 30) + "</body></html>")

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    text = scriptwriter.article_text({
        "title": "Story",
        "url": "https://example.com/story",
        "description": "Short summary.",
    })
    assert len(text) >= 300


def test_source_without_readable_content_uses_gnews_summary(monkeypatch):
    import scriptwriter

    def fake_urlopen(req, timeout=12):
        return _Response("<html><head></head><body>Blocked</body></html>")

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    text = scriptwriter.article_text({
        "title": "Story headline",
        "url": "https://example.com/story",
        "description": "Useful factual summary.",
    })
    assert text == "Story headline. Useful factual summary."


def test_source_requires_evidence(monkeypatch):
    import scriptwriter
    from urllib.error import HTTPError

    def fake_urlopen(req, timeout=12):
        raise HTTPError(req.full_url, 403, "Forbidden", {}, None)

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    try:
        scriptwriter.article_text({
            "title": "Story headline",
            "url": "https://example.com/story",
            "description": "",
        })
    except RuntimeError as exc:
        assert str(exc) == "The selected story has no readable source evidence."
    else:
        raise AssertionError("Expected missing-evidence error")


def test_invalid_source_url_uses_gnews_summary(monkeypatch):
    import scriptwriter

    def fake_urlopen(req, timeout=12):
        raise AssertionError("Publisher URL should not be opened for an invalid URL")

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    text = scriptwriter.article_text({
        "title": "Story headline",
        "url": "not-a-url",
        "description": "GNews summary.",
    })
    assert text == "Story headline. GNews summary."


def test_generation_prompt_has_no_approved_title(monkeypatch):
    import scriptwriter

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    captured = {}

    class Response:
        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, size=-1):
            return b'{"choices":[{"message":{"content":"{\"opening_headline\":\"Rohit Gets Praise\",\"slides\":[{\"voiceover\":\"Rohit Sharma got praise.\"},{\"voiceover\":\"A legend explained why.\"},{\"voiceover\":\"The remark focused on centuries.\"},{\"voiceover\":\"That is the key story detail.\"}],\"titles\":[\"Rohit Sharma Gets Praise\",\"Legend Praises Rohit Sharma\"],\"description\":\"A legend praised Rohit Sharma.\",\"hashtags\":[\"#RohitSharma\",\"#Cricket\"],\"first_comment\":\"Was this the right praise for Rohit?\"}"}}]}'

    def fake_urlopen(req, timeout=45):
        captured["body"] = json.loads(req.data)
        return Response()

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    result = scriptwriter.generate_script(
        {"title": "Indian legend praises Rohit Sharma"},
        "A named Indian legend praised Rohit Sharma.",
    )
    prompt = captured["body"]["messages"][1]["content"]
    assert "Approved YouTube title" not in prompt
    assert "A named Indian legend praised Rohit Sharma." in prompt
    assert result["titles"]
