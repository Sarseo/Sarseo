"""Measure a recitation ASR model against human (مشرف) judgements.

The point of comparison is NOT word error rate on professional reciters —
it is how well the model finds the SAME mistakes a human supervisor marked
on real student recordings. That is what Darajaat already produces in its
`/api/admin/learn/judge` screen (mistake types: miss / sub / vowel / near).

Input: a JSONL file, one judged recording per line:

    {"audio": "rec/abc.wav",          # path to the audio, or
     "text":  "...",                   #   a transcript to score instead of audio
     "sura": 2, "aya_from": 255, "aya_to": 255,
     "mistakes": [                      # the supervisor's verdict (ground truth)
        {"type": "miss", "ref": "2:255:7"},
        {"type": "sub",  "ref": "2:255:9", "said": "..."}
     ]}

`ref` is sura:aya:word (1-based word within the aya). `type` is one of
miss (متروكة), sub (مبدّلة), extra (زائدة), vowel (حركة).

For each recording the engine produces its own mistake list; we compare the
two and count, per mistake type:
  - detected   (TP): supervisor marked it AND engine flagged that word
  - missed     (FN): supervisor marked it, engine stayed silent   → نقص
  - false alarm(FP): engine flagged a word the supervisor left clean → أسوأ خطأ
and report precision / recall per type and overall, plus latency if given.

Run:
    python -m engine.cli bench judged.jsonl                 # uses Whisper ASR on audio
    python -m engine.cli bench judged.jsonl --text          # score the given transcripts
    python -m engine.cli bench judged.jsonl --pred pred.jsonl  # bring your own model's output
"""
from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path

from .align import diff
from .normalize import normalize_text
from .quran import Quran

TYPES = ["miss", "sub", "extra", "vowel"]
LABEL = {"miss": "متروكة", "sub": "مبدّلة", "extra": "زائدة", "vowel": "حركة"}
# engine Op.kind -> benchmark type
OP2TYPE = {"del": "miss", "sub": "sub", "ins": "extra"}


@dataclass
class Case:
    sura: int
    aya_from: int
    aya_to: int
    gold: set            # {(type, ref)} from the supervisor
    text: str | None = None
    audio: str | None = None
    latency_ms: float | None = None


@dataclass
class Tally:
    tp: int = 0
    fp: int = 0
    fn: int = 0

    def precision(self) -> float:
        d = self.tp + self.fp
        return self.tp / d if d else 1.0

    def recall(self) -> float:
        d = self.tp + self.fn
        return self.tp / d if d else 1.0

    def f1(self) -> float:
        p, r = self.precision(), self.recall()
        return 2 * p * r / (p + r) if p + r else 0.0


def load_cases(path: Path) -> list[Case]:
    cases = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        d = json.loads(line)
        gold = {(m["type"], m["ref"]) for m in d.get("mistakes", [])}
        cases.append(Case(
            sura=d["sura"], aya_from=d.get("aya_from", 1), aya_to=d.get("aya_to", d.get("aya_from", 300)),
            gold=gold, text=d.get("text"), audio=d.get("audio"), latency_ms=d.get("latency_ms")))
    return cases


def engine_mistakes(case: Case, q: Quran, transcript: str) -> set:
    """Run the alignment engine, return {(type, ref)} it would flag."""
    expected = q.span(case.sura, case.aya_from, case.aya_to)
    heard = normalize_text(transcript)
    out = set()
    for op in diff(expected, heard):
        t = OP2TYPE.get(op.kind)
        if t and op.expected is not None:
            ref = f"{op.expected.sura}:{op.expected.aya}:{op.expected.pos}"
            out.add((t, ref))
        elif t == "extra" or (op.kind == "ins"):
            out.add(("extra", None))  # extra words have no reference position
    return out


def score(cases: list[Case], preds: dict[int, set]) -> dict:
    """preds[i] = set of (type, ref) the model flagged for cases[i]."""
    # overall counts collapse "extra" refs (None) by matching count, not position
    per = defaultdict(Tally)
    overall = Tally()
    lat = []
    for i, c in enumerate(cases):
        pred = preds.get(i, set())
        gold = c.gold
        # vowel mistakes: Whisper can't see tashkeel, so note coverage separately
        for g in gold:
            t = g[0]
            hit = g in pred
            per[t].tp += hit
            per[t].fn += not hit
            overall.tp += hit
            overall.fn += not hit
        for p in pred:
            if p not in gold:
                per[p[0]].fp += 1
                overall.fp += 1
        if c.latency_ms is not None:
            lat.append(c.latency_ms)
    return {"per": per, "overall": overall, "latency": lat}


def fmt(res: dict, title: str) -> str:
    lines = [f"\n=== {title} ===",
             f"{'نوع الخطأ':<10} {'كشف':>5} {'فات':>5} {'خطأ':>5} {'دقة':>7} {'استرجاع':>9} {'F1':>6}"]
    per, overall = res["per"], res["overall"]
    for t in TYPES:
        if t not in per:
            continue
        x = per[t]
        lines.append(f"{LABEL[t]:<10} {x.tp:>5} {x.fn:>5} {x.fp:>5} "
                     f"{x.precision():>6.0%} {x.recall():>8.0%} {x.f1():>6.2f}")
    o = overall
    lines.append(f"{'الإجمالي':<10} {o.tp:>5} {o.fn:>5} {o.fp:>5} "
                 f"{o.precision():>6.0%} {o.recall():>8.0%} {o.f1():>6.2f}")
    lines.append("  كشف=أخطاء حقيقية وجدها · فات=أخطاء حقيقية تركها · خطأ=تنبيه على كلمة صحيحة")
    if res["latency"]:
        lat = sorted(res["latency"])
        p50 = lat[len(lat) // 2]
        p90 = lat[int(len(lat) * 0.9)]
        lines.append(f"  زمن التنبيه: وسيط {p50:.0f} ملّي ثانية · 90% ≤ {p90:.0f} ملّي ثانية")
    return "\n".join(lines)


def run(path: str, use_text: bool, pred_path: str | None, model: str | None) -> int:
    cases = load_cases(Path(path))
    if not cases:
        print("لا توجد حالات في الملف.")
        return 1
    q = Quran()
    preds: dict[int, set] = {}

    if pred_path:
        # bring-your-own-model: a JSONL aligned line-for-line with the cases,
        # each line {"mistakes": [{"type","ref"}, ...]}
        rows = [json.loads(l) for l in Path(pred_path).read_text(encoding="utf-8").splitlines() if l.strip()]
        for i, r in enumerate(rows):
            preds[i] = {(m["type"], m.get("ref")) for m in r.get("mistakes", [])}
        title = f"نموذجكم (من {Path(pred_path).name})"
    else:
        from .asr import DEFAULT_MODEL, transcribe
        title = f"Whisper ({model or DEFAULT_MODEL})"
        for i, c in enumerate(cases):
            transcript = c.text if (use_text or not c.audio) else transcribe(c.audio, model or DEFAULT_MODEL)
            preds[i] = engine_mistakes(c, q, transcript or "")

    res = score(cases, preds)
    n_vowel = sum(1 for c in cases for g in c.gold if g[0] == "vowel")
    print(fmt(res, title))
    print(f"\nعدد التسجيلات: {len(cases)} · إجمالي الأخطاء المُحكَّمة: {sum(len(c.gold) for c in cases)}")
    if n_vowel and not pred_path:
        print(f"تنبيه: {n_vowel} خطأ حركة (vowel) في البيانات — نموذج Whisper لا يرى التشكيل، "
              f"فاسترجاعه لها صفر بطبيعته. نموذجكم CTC هو الذي يُقاس عليها.")
    return 0
