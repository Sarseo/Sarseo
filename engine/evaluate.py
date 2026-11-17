"""Evaluate ASR + localisation on EveryAyah recordings (one ayah per file).

Metrics: word error rate against the true ayah, and whether the locator
finds the correct ayah without being told where the reciter is.
Note: EveryAyah reciters are part of the model's training data, so these
numbers are optimistic. Use held-out reciters / own recordings for real tests.
"""
from __future__ import annotations

import random
import time
import urllib.request
from pathlib import Path

from .align import Locator, diff
from .asr import DEFAULT_MODEL, transcribe
from .normalize import normalize_text
from .quran import ROOT, Quran

AUDIO_DIR = ROOT / "data" / "audio"


def fetch(reciter: str, sura: int, aya: int) -> Path:
    dest = AUDIO_DIR / reciter / f"{sura:03d}{aya:03d}.mp3"
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(
            f"https://everyayah.com/data/{reciter}/{dest.name}", dest)
    return dest


def run(reciter: str, n: int, seed: int, model: str | None) -> int:
    q = Quran()
    loc = Locator(q.words)
    keys = list(q.ayah_start)
    rng = random.Random(seed)
    sample = rng.sample(keys, n)
    errs = total = located = 0
    t0 = time.time()
    for sura, aya in sample:
        text = transcribe(str(fetch(reciter, sura, aya)), model or DEFAULT_MODEL)
        heard = normalize_text(text)
        expected = q.span(sura, aya)
        ops = diff(expected, heard)
        e = sum(o.kind != "ok" for o in ops)
        errs += e; total += len(expected)
        span = loc.locate(heard)
        # identical wording elsewhere (e.g. 26:2 / 28:2) counts as a hit
        hit = bool(span) and (
            any((w.sura, w.aya) == (sura, aya) for w in q.words[span[0]:span[1]])
            or [w.norm for w in q.words[span[0]:span[1]]] == [w.norm for w in expected])
        located += hit
        print(f"{sura:3d}:{aya:<3d} WER {e/len(expected):5.0%}  located={'ja' if hit else 'NEIN'}")
    dt = time.time() - t0
    print(f"\nWER gesamt: {errs/total:.1%} ({errs}/{total} Wörter)")
    print(f"Ayah gefunden: {located}/{n}")
    print(f"Zeit: {dt:.0f}s ({dt/n:.1f}s pro Ayah, CPU)")
    return 0
