"""Speech recognition with a Quran-fine-tuned Whisper model."""
from __future__ import annotations

import subprocess
from functools import lru_cache

import numpy as np

DEFAULT_MODEL = "tarteel-ai/whisper-base-ar-quran"
SR = 16_000


def load_audio(path: str) -> np.ndarray:
    """Decode any audio file to mono 16 kHz float32 via ffmpeg."""
    out = subprocess.run(
        ["ffmpeg", "-nostdin", "-loglevel", "error", "-i", path,
         "-f", "f32le", "-ac", "1", "-ar", str(SR), "-"],
        capture_output=True, check=True).stdout
    return np.frombuffer(out, np.float32)


@lru_cache(maxsize=2)
def _pipeline(model: str):
    from transformers import GenerationConfig, pipeline
    asr = pipeline("automatic-speech-recognition", model=model,
                   chunk_length_s=30, device="cpu")
    # Tarteel's checkpoints ship an outdated generation config without
    # language tokens; borrow the one of the matching OpenAI base model.
    if "whisper" in model and not hasattr(asr.model.generation_config, "lang_to_id"):
        size = next((s for s in ("tiny", "base", "small", "medium") if s in model), "base")
        asr.model.generation_config = GenerationConfig.from_pretrained(f"openai/whisper-{size}")
    return asr


def transcribe(path: str, model: str = DEFAULT_MODEL) -> str:
    asr = _pipeline(model)
    audio = load_audio(path)
    result = asr({"raw": audio, "sampling_rate": SR},
                 generate_kwargs={"language": "arabic", "task": "transcribe"})
    return result["text"].strip()
