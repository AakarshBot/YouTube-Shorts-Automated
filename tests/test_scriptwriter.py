import json

import pytest

from scriptwriter import EDITORIAL_FINGERPRINT, MAX_SLIDES, MAX_WORDS, MIN_SLIDES, REDO_GUIDANCE, validate_editorial_angles, validate_script


def make_angle(title="Rohit Gets Backing"):
    return {
        "title": title,
        "description": "Focus on the backing Rohit received and why it matters.",
        "evidence_basis": "The source names Sunil Gavaskar and describes his assessment.",
    }


def make_ready(slides=None, headline="Rohit Sharma Praise", angle=None):
    return {
        "status": "ready",
        "reason": "",
        "story_angle": angle or make_angle(),
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
        "story_angle": None,
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


def test_qc_rejects_blank_title_options_and_hashtags():
    result = make_ready()
    result["titles"] = ["Valid title", "   "]
    result["hashtags"] = [""]
    errors = validate_script(result)
    assert "Every title option needs text." in errors
    assert "At least one relevant hashtag is required." in errors


def test_malformed_qc_fields_are_rejected_without_crashing():
    result = make_ready()
    result["titles"] = None
    result["hashtags"] = None
    result["slides"] = None
    errors = validate_script(result)
    assert "Every slide must be an object." in errors
    assert "At least two title options are required." in errors
    assert "At least one relevant hashtag is required." in errors

    result = make_ready()
    result["slides"][0]["voiceover"] = 123
    assert "Every slide needs spoken narration." in validate_script(result)


def test_story_angle_is_required():
    result = make_ready()
    result["story_angle"] = None
    assert "A selected editorial angle is required." in validate_script(result)


def test_editorial_angle_validation_requires_exactly_three():
    base = {"status": "ready", "reason": "", "angles": [make_angle()]}
    assert validate_editorial_angles(base)[0] == "Exactly three editorial angles are required."
    valid = {
        "status": "ready",
        "reason": "",
        "angles": [
            make_angle("Rohit Gets Backing"),
            make_angle("Gavaskar's Key Reason"),
            make_angle("What Changed For India"),
        ],
    }
    assert validate_editorial_angles(valid) == []


def test_editorial_angle_titles_must_be_unique_and_two_to_five_words():
    result = {
        "status": "ready",
        "reason": "",
        "angles": [
            make_angle("Same Angle"),
            make_angle("Same Angle"),
            make_angle("One Two Three Four Five Six"),
        ],
    }
    errors = validate_editorial_angles(result)
    assert "Editorial angle titles must be unique." in errors
    assert "Editorial angle 3 title must contain 2–5 words." in errors


def test_insufficient_evidence_must_return_no_angles():
    result = {
        "status": "needs_more_sources",
        "reason": "The available summary is too thin.",
        "angles": [make_angle()],
    }
    assert "Editorial angles must be empty when more sources are needed." in validate_editorial_angles(result)


class _Response:
    def __init__(self, body, final_url=None):
        self.body = body.encode()
        self.final_url = final_url

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def geturl(self):
        return self.final_url

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
    assert text.startswith("[GNEWS DESCRIPTION FALLBACK — ARTICLE TEXT UNAVAILABLE]")
    assert text.endswith("Story headline. GNews summary.")


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
    assert text.startswith("[GNEWS DESCRIPTION FALLBACK — ARTICLE TEXT UNAVAILABLE]")
    assert text.endswith("Story headline. GNews summary.")


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


def test_editorial_angle_generation_uses_supplied_evidence_and_returns_three(monkeypatch):
    import scriptwriter

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    captured = {}
    generated = {
        "status": "ready",
        "reason": "",
        "angles": [
            make_angle("Rohit Gets Backing"),
            make_angle("Gavaskar's Key Reason"),
            make_angle("What Changed For India"),
        ],
    }
    body = json.dumps({"choices": [{"message": {"content": json.dumps(generated)}}]})

    def fake_urlopen(req, timeout=45):
        captured["body"] = json.loads(req.data)
        return _Response(body)

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    result = scriptwriter.suggest_editorial_angles(
        {"title": "Indian legend praises Rohit Sharma"},
        [{"title": "Source", "url": "https://example.com", "text": "Sunil Gavaskar praises Rohit Sharma."}],
        "Cricket — India / Pakistan / Sri Lanka / Asia",
    )
    assert result == generated
    prompt = captured["body"]["messages"][1]["content"]
    assert "Your first job is editorial selection, not scriptwriting." in prompt
    assert "exactly 3 genuinely different, research-backed editorial angles" in prompt
    assert EDITORIAL_FINGERPRINT in prompt
    assert "Sunil Gavaskar praises Rohit Sharma." in prompt
    assert "Treat marked text as limited evidence." in prompt
    assert "[GNEWS DESCRIPTION FALLBACK — ARTICLE TEXT UNAVAILABLE]" in prompt


def test_editorial_angle_planner_preserves_previous_script_context(monkeypatch):
    import scriptwriter

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    captured = {}
    generated = {
        "status": "ready",
        "reason": "",
        "angles": [
            make_angle("Rohit Gets Backing"),
            make_angle("Gavaskar's Key Reason"),
            make_angle("What Changed For India"),
        ],
    }
    body = json.dumps({"choices": [{"message": {"content": json.dumps(generated)}}]})

    def fake_urlopen(req, timeout=45):
        captured["body"] = json.loads(req.data)
        return _Response(body)

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    scriptwriter.suggest_editorial_angles(
        {"title": "Story"},
        [{"title": "Source", "url": "https://example.com", "text": "A" * 400}],
        "Sports",
        previous=make_ready(headline="Old Script"),
        redo_level=1,
    )
    prompt = captured["body"]["messages"][1]["content"]
    assert "Previous script angle:" in prompt
    assert "The three new angles must be materially different" in prompt
    assert REDO_GUIDANCE[1] in prompt



def test_redo_guidance_escalates_with_each_pass(monkeypatch):
    import scriptwriter

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    captured = {}
    generated = {
        "status": "ready",
        "reason": "",
        "angles": [
            make_angle("Rohit Gets Backing"),
            make_angle("Gavaskar's Key Reason"),
            make_angle("What Changed For India"),
        ],
    }
    body = json.dumps({"choices": [{"message": {"content": json.dumps(generated)}}]})

    def fake_urlopen(req, timeout=45):
        captured["body"] = json.loads(req.data)
        return _Response(body)

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    for level in (1, 2, 3):
        scriptwriter.suggest_editorial_angles(
            {"title": "Story"},
            [{"title": "Source", "url": "https://example.com", "text": "A" * 400}],
            "Sports",
            previous=make_ready(headline="Old Script"),
            redo_level=level,
        )
        prompt = captured["body"]["messages"][1]["content"]
        assert REDO_GUIDANCE[level] in prompt
        for earlier in range(1, level):
            assert REDO_GUIDANCE[earlier] not in prompt


def test_generation_prompt_contains_selected_editorial_angle(monkeypatch):
    import scriptwriter

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    captured = {}
    generated = {
        "status": "ready",
        "reason": "",
        "opening_headline": "Rohit Gets Praise",
        "slides": [
            {"voiceover": "Rohit Sharma got praise."},
            {"voiceover": "His experience was the key reason."},
            {"voiceover": "The source connected it to India's batting."},
            {"voiceover": "That assessment keeps his role central."},
        ],
        "titles": ["Rohit Sharma Gets Praise", "Why Rohit's Experience Matters"],
        "description": "The story.",
        "hashtags": ["#Cricket"],
        "first_comment": "Thoughts?",
    }
    body = json.dumps({"choices": [{"message": {"content": json.dumps(generated)}}]})

    def fake_urlopen(req, timeout=45):
        captured["body"] = json.loads(req.data)
        return _Response(body)

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    angle = make_angle()
    result = scriptwriter.generate_script(
        {"title": "Indian legend praises Rohit Sharma"},
        [{"title": "Source", "url": "https://example.com", "text": "A named source identifies Sunil Gavaskar."}],
        "Cricket — India / Pakistan / Sri Lanka / Asia",
        angle=angle,
        redo_level=2,
    )
    prompt = captured["body"]["messages"][1]["content"]
    assert "SELECTED EDITORIAL ANGLE — AUTHORITATIVE" in prompt
    assert angle["title"] in prompt
    assert "Do not replace it with the obvious event/result summary." in prompt
    assert EDITORIAL_FINGERPRINT in prompt
    assert "[GNEWS DESCRIPTION FALLBACK — ARTICLE TEXT UNAVAILABLE]" in prompt
    assert "Treat marked text as limited evidence." in prompt
    assert REDO_GUIDANCE[2] in prompt
    assert "Cricket — India / Pakistan / Sri Lanka / Asia" in captured["body"]["messages"][0]["content"]
    assert result["story_angle"] == angle


def test_custom_angle_is_authoritative(monkeypatch):
    import scriptwriter

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    captured = {}
    generated = {
        "status": "ready",
        "reason": "",
        "opening_headline": "Custom Story Focus",
        "slides": [
            {"voiceover": "The source revealed a key detail."},
            {"voiceover": "That detail changed how the decision looked."},
            {"voiceover": "The explanation appeared in the public remarks."},
            {"voiceover": "It became the clearest part of the story."},
        ],
        "titles": ["The Key Detail", "Why The Detail Matters"],
        "description": "The key story detail.",
        "hashtags": ["#News"],
        "first_comment": "What stands out to you?",
    }
    body = json.dumps({"choices": [{"message": {"content": json.dumps(generated)}}]})

    def fake_urlopen(req, timeout=45):
        captured["body"] = json.loads(req.data)
        return _Response(body)

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    custom = "Focus on the public explanation rather than the final result."
    result = scriptwriter.generate_script(
        {"title": "Story"},
        [{"title": "Source", "url": "https://example.com", "text": "The source contains a public explanation."}],
        "News",
        angle=custom,
    )
    assert custom in captured["body"]["messages"][1]["content"]
    assert result["story_angle"] == custom


def test_script_only_redo_requests_script_fields_only(monkeypatch):
    import scriptwriter

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    captured = {}
    previous = make_ready(
        slides=[
            {"voiceover": "Original opening."},
            {"voiceover": "Original second fact."},
            {"voiceover": "Original third fact."},
            {"voiceover": "Original ending."},
        ],
        headline="Original Script",
    )
    generated = {
        "status": "ready",
        "reason": "",
        "opening_headline": "New Script",
        "slides": [
            {"voiceover": "New opening."},
            {"voiceover": "New second fact."},
            {"voiceover": "New third fact."},
            {"voiceover": "New ending."},
        ],
    }
    body = json.dumps({"choices": [{"message": {"content": json.dumps(generated)}}]})

    def fake_urlopen(req, timeout=45):
        captured["body"] = json.loads(req.data)
        return _Response(body)

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    angle = make_angle("New editorial spine")
    result = scriptwriter.generate_script(
        {"title": "Story"},
        [{"title": "Source", "url": "https://example.com", "text": "Important source facts."}],
        "Cricket — India / Pakistan / Sri Lanka / Asia",
        previous=previous,
        script_only=True,
        angle=angle,
    )

    schema = captured["body"]["response_format"]["json_schema"]["schema"]
    assert set(schema["properties"]) == {"status", "reason", "opening_headline", "slides"}
    assert "titles" not in schema["properties"]
    assert "description" not in schema["properties"]
    assert "hashtags" not in schema["properties"]
    assert "first_comment" not in schema["properties"]
    prompt = captured["body"]["messages"][1]["content"]
    assert "script-only redo" in prompt
    assert "Do not generate packaging fields" in prompt
    assert angle["title"] in prompt
    assert result["story_angle"] == angle



def test_unresolved_google_news_page_is_not_accepted_as_article_text(monkeypatch):
    import scriptwriter

    url = "https://news.google.com/rss/articles/raw-story-token"
    story = {
        "title": "Story headline",
        "url": url,
        "description": "A short feed description.",
    }

    def fake_urlopen(req, timeout=12):
        landing_page = "<html><article>" + ("Google News page furniture. " * 30) + "</article></html>"
        return _Response(landing_page, final_url=url)

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    text = scriptwriter.article_text(story)

    assert text.startswith("[GNEWS DESCRIPTION FALLBACK — ARTICLE TEXT UNAVAILABLE]")
    assert "Google News page furniture" not in text
    assert story["url"] == url


def test_google_news_http_redirect_preserves_exact_publisher_url(monkeypatch):
    import scriptwriter

    publisher_url = "https://Example.com/Story/ABC?Param=Value"
    story = {
        "title": "Story headline",
        "url": "https://news.google.com/rss/articles/raw-story-token",
        "description": "A short feed description.",
    }

    def fake_urlopen(req, timeout=12):
        article = "<html><article>" + ("Important publisher article fact. " * 30) + "</article></html>"
        return _Response(article, final_url=publisher_url)

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    text = scriptwriter.article_text(story)

    assert text.startswith("Important publisher article fact.")
    assert story["url"] == publisher_url


# Deterministic prompt/contract coverage across the actual desk labels.
DESK_STORY_CASES = [
    (
        "Cricket — India / Pakistan / Sri Lanka / Asia",
        "Fictional batter changes approach after injury return",
        "In the fictional Coastal Cup, batter Arin Rao returned after a wrist injury and scored 61 from 38 balls. Coach Leela Sen said a lower backlift helped him handle the new ball.",
        "Backlift Changed The Return",
        "Arin Rao",
    ),
    (
        "Cricket — Global",
        "Fictional captain reshapes bowling plan",
        "In a fictional international series, captain Noah Vale used spinner Eli Hart for two powerplay overs and took a wicket. The opposing side delayed its attack because the change brought a left-right matchup.",
        "A Powerplay Matchup",
        "Noah Vale",
    ),
    (
        "Niche Sports — Global",
        "Fictional tennis player changes return position",
        "In a fictional tennis final, Mira Sol moved inside the baseline on second serves and won 71% of return points. Coach Ivo Ren said the position change forced opponents to hit earlier and reduced their angles.",
        "Inside The Baseline",
        "Mira Sol",
    ),
    (
        "News",
        "Fictional council revises transit vote",
        "In fictional Northbridge, the council voted 7–2 to fund two late bus routes by shifting money from a lightly used service. The published note says the new routes will connect three hospital shifts with the central station.",
        "The Funding Tradeoff",
        "Northbridge Council",
    ),
    (
        "Technology",
        "Fictional AI lab cuts inference cost",
        "Fictional startup Kestrel AI says a smaller retrieval step cut average inference cost by 28% across 500 customer tasks. Its release notes report no change to the base model and list the benchmark limits.",
        "Cheaper Retrieval Step",
        "Kestrel AI",
    ),
    (
        "Entertainment",
        "Fictional drama shifts release strategy",
        "Fictional streamer RaagaPlay will release the drama Dusk Line weekly instead of dropping all six episodes together. The company says its pilot completion rate rose 31% when viewers had a new episode to discuss.",
        "A Weekly Release",
        "RaagaPlay",
    ),
    (
        "Business & Finance",
        "Fictional retailer changes supply model",
        "Fictional retailer Northstar reported an 18% rise in quarterly revenue after moving regional inventory closer to local warehouses. Its filing attributes most of the change to faster delivery and fewer cancelled orders.",
        "Faster Regional Delivery",
        "Northstar",
    ),
    (
        "Gaming",
        "Fictional game changes beta progression",
        "Fictional studio Ember Forge changed its game's beta progression so new players unlock equipment through short challenges rather than long quests. Test notes show more players finished the first session after the change.",
        "Shorter First Session",
        "Ember Forge",
    ),
    (
        "Science & Space",
        "Fictional probe finds buried ice",
        "Fictional probe Kestrel-2 detected a stronger-than-expected radar signal beneath the surface of a polar crater. Mission notes say the instrument cannot yet distinguish water ice from other reflective material.",
        "What The Signal Means",
        "Kestrel-2",
    ),
]


def test_desk_fixtures_match_the_dashboard_handoff_values():
    from topic_fetcher import DESKS

    dashboard_values = set(DESKS)
    dashboard_values.update(DESKS["Sports"])
    assert {case[0] for case in DESK_STORY_CASES} <= dashboard_values


def test_needs_more_sources_schema_allows_empty_angles(monkeypatch):
    import scriptwriter

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    captured = {}
    generated = {
        "status": "needs_more_sources",
        "reason": "The feed summary contains no usable supporting detail.",
        "angles": [],
    }
    body = json.dumps({"choices": [{"message": {"content": json.dumps(generated)}}]})

    def fake_urlopen(req, timeout=45):
        captured["body"] = json.loads(req.data)
        return _Response(body)

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    result = scriptwriter.suggest_editorial_angles(
        {"title": "Thin feed headline"},
        [{
            "title": "Thin feed headline",
            "url": "https://example.com/thin",
            "text": "[GNEWS DESCRIPTION FALLBACK — ARTICLE TEXT UNAVAILABLE]\nThin feed headline. One brief feed description.",
        }],
        "Politics & Policy",
    )

    schema = captured["body"]["response_format"]["json_schema"]["schema"]
    assert "minItems" not in schema["properties"]["angles"]
    assert "maxItems" not in schema["properties"]["angles"]
    assert result == generated
    assert "an empty angles array" in captured["body"]["messages"][1]["content"]


@pytest.mark.parametrize("desk,title,evidence,angle_title,lead", DESK_STORY_CASES)
def test_scriptwriter_contract_is_desk_aware(monkeypatch, desk, title, evidence, angle_title, lead):
    import scriptwriter

    monkeypatch.setenv("GROQ_API_KEY", "test-key")
    captured = []
    angle_result = {
        "status": "ready",
        "reason": "",
        "angles": [
            {
                "title": angle_title,
                "description": f"Focus on the supported detail behind {title.lower()}.",
                "evidence_basis": evidence.split(". ")[0] + ".",
            },
            {
                "title": "The Wider Context",
                "description": "Focus on the broader context provided by the source.",
                "evidence_basis": evidence.split(". ")[1].rstrip(".") + ".",
            },
            {
                "title": "The Other Factor",
                "description": "Focus on a different fact in the report.",
                "evidence_basis": evidence.split(". ")[0] + ".",
            },
        ],
    }
    first_sentence, second_sentence = evidence.split(". ", 1)
    script_result = {
        "status": "ready",
        "reason": "",
        "opening_headline": angle_title,
        "slides": [
            {"voiceover": f"{lead} made a revealing change."},
            {"voiceover": first_sentence + "."},
            {"voiceover": second_sentence},
            {"voiceover": f"The evidence explains the {angle_title.lower()} focus."},
        ],
        "titles": ["The Hidden Change", "What The Detail Changed"],
        "description": f"A closer look at {title.lower()} and the evidence behind it.",
        "hashtags": ["#Explainer"],
        "first_comment": f"What stands out to you about {angle_title.lower()}?",
    }
    responses = [
        json.dumps({"choices": [{"message": {"content": json.dumps(angle_result)}}]}),
        json.dumps({"choices": [{"message": {"content": json.dumps(script_result)}}]}),
    ]

    def fake_urlopen(req, timeout=45):
        payload = json.loads(req.data)
        captured.append(payload)
        return _Response(responses[len(captured) - 1])

    monkeypatch.setattr(scriptwriter, "urlopen", fake_urlopen)
    story = {"title": title, "url": "https://example.com/fixture"}
    sources = [{"title": title, "url": story["url"], "text": evidence}]

    angles = scriptwriter.suggest_editorial_angles(story, sources, desk)
    assert scriptwriter.validate_editorial_angles(angles) == []
    angle = angles["angles"][0]
    result = scriptwriter.generate_script(story, sources, desk, angle=angle)

    assert scriptwriter.validate_script(result) == []
    assert result["story_angle"] == angle
    assert len(captured) == 2
    assert captured[0]["messages"][0]["content"] == f"You are an experienced editor for the {desk} desk. Source evidence controls factual claims."
    assert captured[1]["messages"][0]["content"] == f"You are an experienced editor for the {desk} desk. Source evidence controls factual claims."
    assert desk in captured[0]["messages"][1]["content"]
    assert desk in captured[1]["messages"][1]["content"]
    assert evidence in captured[0]["messages"][1]["content"]
    assert evidence in captured[1]["messages"][1]["content"]
    assert angle_title in captured[1]["messages"][1]["content"]
    assert "SELECTED EDITORIAL ANGLE — AUTHORITATIVE" in captured[1]["messages"][1]["content"]



def test_related_sources_keep_resolved_publisher_urls(monkeypatch):
    import scriptwriter

    class FakeGNews:
        def __init__(self, **kwargs):
            pass

        def get_news(self, title):
            return [{
                "title": "Related report",
                "url": "https://news.google.com/rss/articles/raw-token",
                "publisher": "Example",
                "description": "Related description",
            }]

    monkeypatch.setattr(scriptwriter, "GNews", FakeGNews)

    def fake_article_text(source):
        source["url"] = "https://Example.com/Story?ID=abc"
        return "Readable publisher article text. " * 20

    monkeypatch.setattr(scriptwriter, "article_text", fake_article_text)
    result = scriptwriter.find_related_sources({
        "title": "Story",
        "url": "https://example.com/primary",
    })
    assert result[0]["url"] == "https://Example.com/Story?ID=abc"


def test_manual_sources_keep_resolved_publisher_urls_and_deduplicate(monkeypatch):
    import scriptwriter

    def fake_article_text(source):
        source["url"] = "https://Example.com/Story?ID=abc"
        return "Readable publisher article text. " * 20

    monkeypatch.setattr(scriptwriter, "article_text", fake_article_text)
    result = scriptwriter.manual_sources([
        "https://news.google.com/rss/articles/raw-token",
        "https://news.google.com/rss/articles/another-token",
    ])
    assert len(result) == 1
    assert result[0]["url"] == "https://Example.com/Story?ID=abc"
