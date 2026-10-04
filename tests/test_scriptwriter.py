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


def test_google_news_redirect_url_is_resolved(monkeypatch):
    import scriptwriter

    calls = []

    def fake_urlopen(req, timeout=12):
        calls.append(req.full_url)
        if "batchexecute" in req.full_url:
            return _Response('[[\"garturlres\",\"https://example.com/story\",]]')
        return _Response("<html><article>""" + ("Important article fact. " * 30) + """</article></html>")

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    text = scriptwriter.article_text(
        "https://news.google.com/rss/articles/test-token?oc=5"
    )
    assert len(text) >= 300
    assert calls[0].startswith("https://news.google.com/_/DotsSplashUi/data/batchexecute")
    assert calls[1] == "https://example.com/story"


def test_google_news_legacy_url_query_is_resolved(monkeypatch):
    import scriptwriter

    calls = []

    def fake_urlopen(req, timeout=12):
        calls.append(req.full_url)
        return _Response("<html><article>""" + ("Important article fact. " * 30) + """</article></html>")

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    text = scriptwriter.article_text(
        "https://news.google.com/news/url?url=https%3A%2F%2Fexample.com%2Fstory&oc=5"
    )
    assert len(text) >= 300
    assert calls == ["https://example.com/story"]
