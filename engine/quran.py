"""Quran text download and SQLite word index.

Text source: Tanzil Project (https://tanzil.net), CC BY 3.0, verbatim.
Downloaded at build time; not committed to the repository.
"""
from __future__ import annotations

import sqlite3
import urllib.request
from dataclasses import dataclass
from functools import cached_property
from pathlib import Path

from .normalize import normalize_word, tokenize

ROOT = Path(__file__).resolve().parent.parent
RAW_DIR = ROOT / "data" / "raw"
DB_PATH = ROOT / "data" / "quran.db"
TANZIL_URL = (
    "https://tanzil.net/pub/download/index.php?marks=true&sajdah=true"
    "&rub=false&tatweel=false&quranType=simple&outType=txt-2&agree=true"
)


@dataclass(frozen=True)
class Word:
    idx: int      # global position 0..N-1
    sura: int
    aya: int
    pos: int      # 1-based position within aya
    text: str     # display form (with tashkeel)
    norm: str     # normalized form for matching


def download(dest: Path = RAW_DIR / "quran-simple.txt") -> Path:
    if not dest.exists():
        dest.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(TANZIL_URL, dest)
    return dest


def parse(path: Path) -> list[tuple[int, int, str]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line or not line[0].isdigit():
            continue
        s, a, text = line.split("|", 2)
        rows.append((int(s), int(a), text))
    return rows


def build_db(src: Path | None = None, db: Path = DB_PATH) -> Path:
    rows = parse(src or download())
    db.parent.mkdir(parents=True, exist_ok=True)
    db.unlink(missing_ok=True)
    con = sqlite3.connect(db)
    con.executescript("""
        CREATE TABLE ayah (sura INT, aya INT, text TEXT, PRIMARY KEY (sura, aya));
        CREATE TABLE word (idx INT PRIMARY KEY, sura INT, aya INT, pos INT,
                           text TEXT, norm TEXT);
        CREATE INDEX word_norm ON word(norm);
    """)
    con.executemany("INSERT INTO ayah VALUES (?,?,?)", rows)
    words, idx = [], 0
    for s, a, text in rows:
        for pos, tok in enumerate(tokenize(text), 1):
            words.append((idx, s, a, pos, tok, normalize_word(tok)))
            idx += 1
    con.executemany("INSERT INTO word VALUES (?,?,?,?,?,?)", words)
    con.commit()
    con.close()
    return db


class Quran:
    def __init__(self, db: Path = DB_PATH):
        if not db.exists():
            build_db(db=db)
        con = sqlite3.connect(db)
        self.words = [Word(*r) for r in con.execute(
            "SELECT idx, sura, aya, pos, text, norm FROM word ORDER BY idx")]
        con.close()

    @cached_property
    def ayah_start(self) -> dict[tuple[int, int], int]:
        out: dict[tuple[int, int], int] = {}
        for w in self.words:
            out.setdefault((w.sura, w.aya), w.idx)
        return out

    def span(self, sura: int, aya_from: int, aya_to: int | None = None) -> list[Word]:
        aya_to = aya_to or aya_from
        return [w for w in self.words
                if w.sura == sura and aya_from <= w.aya <= aya_to]
