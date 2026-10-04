from scriptwriter import validate_script


def script(headline="A Real Story Now", slides=None):
    return {
        "opening_headline": headline,
        "slides": slides or [{"voiceover": "One clear fact. "}] * 4,
    }


def test_valid_four_slide_script():
    result = script(
        slides=[
            {"voiceover": "India made history with this result."},
            {"voiceover": "The key moment changed the contest."},
            {"voiceover": "That result came after a major performance."},
            {"voiceover": "The outcome now sets up what happens next."},
        ]
    )
    assert validate_script(result, "India Make History") == []


def test_valid_five_slide_script():
    result = script(
        slides=[{"voiceover": f"Important fact {i}"} for i in range(5)]
    )
    assert validate_script(result, "A Different Angle") == []


def test_first_slide_must_be_under_fourteen_words():
    result = script(
        slides=[
            {"voiceover": "One two three four five six seven eight nine ten eleven twelve thirteen fourteen"},
            {"voiceover": "Second fact"},
            {"voiceover": "Third fact"},
            {"voiceover": "Fourth fact"},
        ]
    )
    assert "Slide 1 must contain fewer than 14 words." in validate_script(result, "Title")


def test_opening_headline_must_be_three_or_four_words():
    assert "Opening headline must contain exactly 3 or 4 words." in validate_script(
        script("Two Words"), "Title"
    )
    result = script(
        "Four Important Words",
        slides=[
            {"voiceover": "First useful fact"},
            {"voiceover": "Second useful fact"},
            {"voiceover": "Third useful fact"},
            {"voiceover": "Fourth useful fact"},
        ],
    )
    assert validate_script(result, "Title") == []


def test_narration_must_fit_thirty_second_target():
    long = " ".join(["word"] * 76)
    result = script(slides=[{"voiceover": long}] * 4)
    assert "Total narration is too long for the 30-second target." in validate_script(
        result, "Title"
    )


def test_duplicate_slides_are_rejected():
    result = script(slides=[{"voiceover": "Same line"}] * 4)
    assert "Slides must not be duplicated." in validate_script(result, "Title")


def test_missing_approved_title_is_rejected():
    result = script()
    assert validate_script(result, "") == ["Approved title is missing."]


class _Response:
    def __init__(self, text):
        self.text = text.encode()

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, size=-1):
        return self.text


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

    def fake_urlopen(req, timeout=12):
        from urllib.error import HTTPError
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

    def fake_urlopen(req, timeout=12):
        from urllib.error import HTTPError
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
