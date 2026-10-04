import audio
import pytest

def test_audio_module_imports_without_tts_stack():
    assert audio.MODEL is None

def test_audio_requires_script_slides_before_loading_tts():
    with pytest.raises(ValueError, match="no slides"):
        audio.generate_audio({"slides": []})
