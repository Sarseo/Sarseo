import pytest

from engine.align import Locator, diff
from engine.cli import analyse
from engine.normalize import normalize_text, normalize_word
from engine.quran import RAW_DIR, Quran


def test_normalize_removes_tashkeel_and_unifies_alef():
    assert normalize_word("ٱلْحَمْدُ") == "الحمد"
    assert normalize_word("ٱلْكِتَـٰبُ") == normalize_word("الكتاب") == "الكتب"
    assert normalize_word("إِيَّاكَ") == "ايك"
    assert normalize_word("ۚ") == ""
    assert normalize_text("ذَٰلِكَ ٱلْكِتَـٰبُ لَا رَيْبَ ۛ فِيهِ") == ["ذلك", "الكتب", "ل", "ريب", "فيه"]


@pytest.fixture(scope="module")
def q():
    if not (RAW_DIR / "quran-simple.txt").exists():
        pytest.skip("Quran text not downloaded (run: python -m engine.cli build-db)")
    return Quran()


def test_word_count(q):
    assert len(q.ayah_start) == 6236
    assert q.span(1, 1)[0].norm == "بسم"


def test_diff_detects_mistakes(q):
    exp = q.span(1, 2, 4)  # الحمد لله رب العالمين الرحمن الرحيم مالك يوم الدين
    heard = normalize_text("الحمد لله رب العالمين الرحيم ملك يوم الدين امين")
    kinds = [o.kind for o in diff(exp, heard)]
    assert kinds.count("del") == 1        # الرحمن missed
    assert kinds.count("ins") == 1        # امين extra
    assert kinds.count("ok") == 8         # ملك == مالك after normalization


def test_locator_finds_ayat_al_kursi(q):
    heard = normalize_text("الله لا اله الا هو الحي القيوم لا تاخذه سنه ولا نوم")
    s, e = Locator(q.words).locate(heard)
    assert (q.words[s].sura, q.words[s].aya) == (2, 255)


def test_analyse_with_wrong_word(q):
    rep = analyse("قل هو الله احد الله الصمد لم يلد ولم يولد ولم يكن له كفوا واحد", q)
    assert rep.span == "112:1–112:4"
    wrong = [m for m in rep.mistakes() if m.kind == "sub"]
    assert len(wrong) == 1 and wrong[0].expected.norm == "احد"
