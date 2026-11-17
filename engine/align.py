"""Locate recited words in the Quran and diff them word by word."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass

from rapidfuzz.distance import Levenshtein

from .quran import Word

# Words at least this similar (0..1) count as the same word (ASR noise).
MATCH = 0.8


def similarity(a: str, b: str) -> float:
    return Levenshtein.normalized_similarity(a, b)


@dataclass
class Op:
    kind: str                 # "ok" | "sub" | "del" (missed) | "ins" (extra)
    expected: Word | None
    heard: str | None
    score: float = 1.0


def diff(expected: list[Word], heard: list[str]) -> list[Op]:
    """Word-level edit alignment with fuzzy substitution cost."""
    n, m = len(expected), len(heard)
    cost = [[0.0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        cost[i][0] = i
    for j in range(1, m + 1):
        cost[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            sim = similarity(expected[i - 1].norm, heard[j - 1])
            sub = 0.0 if sim >= MATCH else 1.0 - sim * 0.5
            cost[i][j] = min(cost[i - 1][j - 1] + sub,
                             cost[i - 1][j] + 1,
                             cost[i][j - 1] + 1)
    ops: list[Op] = []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            sim = similarity(expected[i - 1].norm, heard[j - 1])
            sub = 0.0 if sim >= MATCH else 1.0 - sim * 0.5
            if abs(cost[i][j] - (cost[i - 1][j - 1] + sub)) < 1e-9:
                ops.append(Op("ok" if sub == 0 else "sub", expected[i - 1], heard[j - 1], sim))
                i, j = i - 1, j - 1
                continue
        if i > 0 and abs(cost[i][j] - (cost[i - 1][j] + 1)) < 1e-9:
            ops.append(Op("del", expected[i - 1], None, 0.0))
            i -= 1
        else:
            ops.append(Op("ins", None, heard[j - 1], 0.0))
            j -= 1
    ops.reverse()
    return ops


class Locator:
    """Find where in the Quran a sequence of heard words most likely is."""

    def __init__(self, words: list[Word], n: int = 3):
        self.words, self.n = words, n
        self.index: dict[tuple[str, ...], list[int]] = defaultdict(list)
        norms = [w.norm for w in words]
        for i in range(len(norms) - n + 1):
            self.index[tuple(norms[i:i + n])].append(i)
        self.unigram: dict[str, list[int]] = defaultdict(list)
        for i, w in enumerate(norms):
            self.unigram[w].append(i)

    def _candidates(self, heard: list[str]) -> Counter:
        votes: Counter = Counter()
        grams = [tuple(heard[k:k + self.n]) for k in range(len(heard) - self.n + 1)]
        for k, g in enumerate(grams):
            hits = self.index.get(g, [])
            if len(hits) > 200:          # too generic
                continue
            for start in hits:
                votes[start - k] += 1
        if not votes:                     # fallback: rare single words
            for k, w in enumerate(heard):
                hits = self.unigram.get(w, [])
                if 0 < len(hits) <= 50:
                    for start in hits:
                        votes[start - k] += 1
        return votes

    def _fit(self, s: int, e: int, heard: list[str]) -> tuple[int, int, int]:
        """Diff a padded window, trim unrecited edges; return (s, e, errors)."""
        ops = diff(self.words[s:e], heard)
        while ops and ops[0].kind == "del":
            ops.pop(0); s += 1
        while ops and ops[-1].kind == "del":
            ops.pop(); e -= 1
        return s, e, sum(op.kind != "ok" for op in ops)

    def locate(self, heard: list[str], top: int = 10) -> tuple[int, int] | None:
        """Return (start_idx, end_idx_exclusive) of best matching span."""
        if not heard:
            return None
        pad = max(3, len(heard) // 4)
        best, best_cost = None, float("inf")
        for start, _ in self._candidates(heard).most_common(top):
            s = max(0, start - pad)
            e = min(len(self.words), start + len(heard) + pad)
            s, e, c = self._fit(s, e, heard)
            if c < best_cost:
                best, best_cost = (s, e), c
        return best
