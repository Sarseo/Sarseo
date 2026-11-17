"""Arabic normalization used for matching (never for display)."""
import re

# Harakat, Quranic annotation marks, superscript alef, tatweel
_DIACRITICS = re.compile(r"[ؐ-ًؚ-ٰٟۖ-ۭـ]")
_ARABIC_LETTER = re.compile(r"[ء-يٱ]")
_MAP = str.maketrans({
    "أ": "ا", "إ": "ا", "آ": "ا", "ٱ": "ا", "ٲ": "ا", "ٳ": "ا",
    "ى": "ي", "ئ": "ي", "ؤ": "و", "ة": "ه",
})


def normalize_word(word: str) -> str:
    w = _DIACRITICS.sub("", word).translate(_MAP)
    w = re.sub(r"[^ء-ي]", "", w.replace("ء", ""))
    # Drop non-initial alef: Uthmani (ذٰلك) vs. standard (ذلك/ذالك) spelling.
    return w[:1] + w[1:].replace("ا", "")


def tokenize(text: str) -> list[str]:
    """Split into words, dropping pause marks / symbols without letters."""
    return [t for t in text.split() if _ARABIC_LETTER.search(t)]


def normalize_text(text: str) -> list[str]:
    return [n for n in (normalize_word(t) for t in tokenize(text)) if n]
