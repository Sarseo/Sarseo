import pytest
from fastapi.testclient import TestClient

from engine.quran import RAW_DIR

pytestmark = pytest.mark.skipif(not (RAW_DIR / "quran-simple.txt").exists(),
                                reason="Quran text not downloaded")


def test_check_text():
    from server.app import app
    c = TestClient(app)
    r = c.post("/v1/check-text", json={"text": "قل هو الله احد الله الصمد لم يلد ولم يولد"})
    assert r.status_code == 200
    d = r.json()
    assert d["span"] == "112:1–112:3" and d["accuracy"] == 1.0


def test_check_text_with_range_reports_missing():
    from server.app import app
    c = TestClient(app)
    r = c.post("/v1/check-text", json={"text": "قل هو الله احد", "sura": 112, "from": 1, "to": 2})
    d = r.json()
    assert d["counts"]["del"] == 2 and d["mistakes"][0]["ref"] == "112:2:1"
