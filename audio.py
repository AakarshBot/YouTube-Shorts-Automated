from hashlib import sha1
from pathlib import Path
import os
import re

MODEL = None
MODEL_KIND = None
ROOT = Path(__file__).resolve().parent
OUTPUT_ROOT = ROOT / "generated_audio"
REFERENCE = Path(os.getenv("AUDIO_REFERENCE", ROOT / "audio_reference.wav"))

def generate_audio(version, run_number=1):
    global MODEL, MODEL_KIND
    slides = version.get("slides") or []
    if not slides:
        raise ValueError("The approved Scriptwriter version has no slides.")

    try:
        import torch
        import torchaudio
        from chatterbox.tts_turbo import ChatterboxTurboTTS
    except ImportError as exc:
        raise RuntimeError("Chatterbox Audio is not installed in this environment. Install the approved local Audio dependencies and run the app again.") from exc

    device = "cuda" if torch.cuda.is_available() else "cpu"
    kind = "turbo" if device == "cuda" else "nano"
    if MODEL is None or MODEL_KIND != kind:
        MODEL = ChatterboxTurboTTS.from_pretrained(device=device, nano=kind == "nano")
        MODEL_KIND = kind

    key = sha1(" ".join(slide["voiceover"] for slide in slides).encode()).hexdigest()[:12]
    output_dir = OUTPUT_ROOT / key
    output_dir.mkdir(parents=True, exist_ok=True)
    for file in output_dir.glob("*.wav"):
        file.unlink()

    reference = REFERENCE if REFERENCE.is_file() else None
    if reference:
        MODEL.prepare_conditionals(str(reference), exaggeration=0.5)

    waves = []
    paths = []
    durations = []

    for number, slide in enumerate(slides, 1):
        text = re.sub(r"\s+", " ", str(slide.get("voiceover", ""))).strip()
        if not text:
            raise ValueError(f"Slide {number} has no voiceover.")
        seed = run_number * 100 + number
        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)

        temperature = 0.8
        if number == 1:
            temperature = 0.88
        elif number == len(slides):
            temperature = 0.84

        wav = MODEL.generate(text, temperature=temperature)

        wav = wav.detach().cpu()
        if wav.ndim == 1:
            wav = wav.unsqueeze(0)
        waves.append(wav)
        durations.append(wav.shape[-1] / MODEL.sr)

    gap_samples = int(MODEL.sr * 0.08)
    raw_duration = sum(durations) + max(0, len(waves) - 1) * 0.08
    if raw_duration > 30:
        try:
            import librosa
            rate = min(1.05, raw_duration / 29.7)
            waves = [
                torch.from_numpy(
                    librosa.effects.time_stretch(wave.squeeze(0).numpy(), rate=rate)
                ).unsqueeze(0)
                for wave in waves
            ]
        except ImportError as exc:
            raise RuntimeError("Audio is over 30 seconds and librosa is missing from the Chatterbox installation.") from exc

    final_duration = sum(wave.shape[-1] / MODEL.sr for wave in waves) + max(0, len(waves) - 1) * 0.08
    if final_duration > 30.5:
        raise RuntimeError("The generated narration is too long to fit the 30-second Short even with slight speed adjustment.")

    for number, wav in enumerate(waves, 1):
        path = output_dir / f"slide_{number:02d}.wav"
        torchaudio.save(str(path), wav, MODEL.sr)
        paths.append(str(path))

    silence = torch.zeros((1, gap_samples))
    combined = []
    for number, wav in enumerate(waves):
        combined.append(wav)
        if number < len(waves) - 1:
            combined.append(silence)
    combined = torch.cat(combined, dim=-1)
    peak = combined.abs().max()
    if peak.item() > 0:
        combined = combined * (0.94 / peak)
    full_path = output_dir / "full.wav"
    torchaudio.save(str(full_path), combined, MODEL.sr)

    return {
        "full_path": str(full_path),
        "slide_paths": paths,
        "duration": combined.shape[-1] / MODEL.sr,
        "model": f"Chatterbox-{kind.title()}",
        "reference": str(reference) if reference else "Built-in Chatterbox voice",
    }
