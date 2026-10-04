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
