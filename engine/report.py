"""Turn a word diff into a recitation report."""
from __future__ import annotations

from dataclasses import dataclass, field

from .align import Op

LABEL = {"ok": "richtig", "sub": "falsch", "del": "ausgelassen", "ins": "zusätzlich"}
# Mistake type names used by Darajaat (app.darajaat.de): miss / sub / extra
# ("vowel" = tashkeel error and "near" = unclear follow once the engine detects them).
API_TYPE = {"sub": "sub", "del": "miss", "ins": "extra"}


@dataclass
class Report:
    ops: list[Op]
    heard_text: str = ""
    counts: dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        self.counts = {k: sum(o.kind == k for o in self.ops) for k in LABEL}

    @property
    def expected_words(self) -> int:
        return sum(o.expected is not None for o in self.ops)

    @property
    def accuracy(self) -> float:
        return self.counts["ok"] / self.expected_words if self.expected_words else 0.0

    @property
    def span(self) -> str:
        ws = [o.expected for o in self.ops if o.expected]
        if not ws:
            return "-"
        a, b = ws[0], ws[-1]
        return f"{a.sura}:{a.aya}" + ("" if (a.sura, a.aya) == (b.sura, b.aya) else f"–{b.sura}:{b.aya}")

    def mistakes(self) -> list[Op]:
        return [o for o in self.ops if o.kind != "ok"]

    def to_dict(self) -> dict:
        return {
            "span": self.span,
            "accuracy": round(self.accuracy, 3),
            "counts": {"ok": self.counts["ok"], **{API_TYPE[k]: self.counts[k] for k in API_TYPE}},
            "heard": self.heard_text,
            "mistakes": [{
                "type": API_TYPE[o.kind],
                "ref": f"{o.expected.sura}:{o.expected.aya}:{o.expected.pos}" if o.expected else None,
                "expected": o.expected.text if o.expected else None,
                "heard": o.heard,
            } for o in self.mistakes()],
        }

    def to_text(self) -> str:
        lines = [f"Stelle: {self.span}   Genauigkeit: {self.accuracy:.0%}   "
                 + "  ".join(f"{LABEL[k]}: {v}" for k, v in self.counts.items())]
        for o in self.mistakes():
            ref = f"{o.expected.sura}:{o.expected.aya}:{o.expected.pos}" if o.expected else "     "
            exp = o.expected.text if o.expected else "—"
            lines.append(f"  [{LABEL[o.kind]:<11}] {ref:<9} erwartet: {exp}   gehört: {o.heard or '—'}")
        return "\n".join(lines)
