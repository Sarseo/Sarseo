"""Sarseo phase-0 CLI.

  python -m engine.cli build-db
  python -m engine.cli check AUDIO [--sura S --from A --to B] [--json]
  python -m engine.cli check-text "TEXT" [--sura S --from A --to B]
  python -m engine.cli eval [--reciter Alafasy_128kbps] [--n 20]
"""
from __future__ import annotations

import argparse
import json
import sys

from .align import Locator, diff
from .normalize import normalize_text
from .quran import Quran, build_db
from .report import Report


def analyse(heard_text: str, q: Quran, sura=None, aya_from=None, aya_to=None) -> Report:
    heard = normalize_text(heard_text)
    if sura:
        expected = q.span(sura, aya_from or 1, aya_to or aya_from or 300)
    else:
        loc = Locator(q.words).locate(heard)
        expected = q.words[loc[0]:loc[1]] if loc else []
    return Report(diff(expected, heard), heard_text)


def _span_args(p):
    p.add_argument("--sura", type=int)
    p.add_argument("--from", dest="aya_from", type=int)
    p.add_argument("--to", dest="aya_to", type=int)
    p.add_argument("--json", action="store_true")


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(prog="sarseo")
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("build-db")
    p = sub.add_parser("check"); p.add_argument("audio"); p.add_argument("--model"); _span_args(p)
    p = sub.add_parser("check-text"); p.add_argument("text"); _span_args(p)
    p = sub.add_parser("eval")
    p.add_argument("--reciter", default="Alafasy_128kbps")
    p.add_argument("--n", type=int, default=20)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--model")
    a = ap.parse_args(argv)

    if a.cmd == "build-db":
        print(build_db())
        return 0
    if a.cmd == "eval":
        from .evaluate import run
        return run(a.reciter, a.n, a.seed, a.model)

    q = Quran()
    if a.cmd == "check":
        from .asr import DEFAULT_MODEL, transcribe
        text = transcribe(a.audio, a.model or DEFAULT_MODEL)
    else:
        text = a.text
    rep = analyse(text, q, a.sura, a.aya_from, a.aya_to)
    print(json.dumps(rep.to_dict(), ensure_ascii=False, indent=2) if a.json else rep.to_text())
    return 0


if __name__ == "__main__":
    sys.exit(main())
