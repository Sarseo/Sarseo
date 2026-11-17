"""HTTP API of the Sarseo engine — the integration point for Darajaat.

  uvicorn server.app:app --port 8000

POST /v1/check         multipart: audio (file), sura?, from?, to?   → Report JSON
POST /v1/check-text    JSON: {"text": "...", "sura"?, "from"?, "to"?} → Report JSON
GET  /v1/health
"""
from __future__ import annotations

import os
import tempfile

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from engine.cli import analyse
from engine.quran import Quran

ORIGINS = os.environ.get(
    "SARSEO_ORIGINS", "https://app.darajaat.de,https://claude.ai,http://localhost:3000"
).split(",")

app = FastAPI(title="Sarseo", version="0.1")
app.add_middleware(CORSMiddleware, allow_origins=ORIGINS,
                   allow_methods=["GET", "POST"], allow_headers=["*"])
_quran: Quran | None = None


def quran() -> Quran:
    global _quran
    if _quran is None:
        _quran = Quran()
    return _quran


class TextIn(BaseModel):
    text: str = Field(min_length=1, max_length=20_000)
    sura: int | None = Field(None, ge=1, le=114)
    from_: int | None = Field(None, alias="from", ge=1)
    to: int | None = Field(None, ge=1)


@app.get("/v1/health")
def health():
    return {"ok": True}


@app.post("/v1/check-text")
def check_text(body: TextIn):
    rep = analyse(body.text, quran(), body.sura, body.from_, body.to)
    if not rep.ops:
        raise HTTPException(422, "Stelle im Quran nicht gefunden")
    return rep.to_dict()


@app.post("/v1/check")
async def check_audio(audio: UploadFile = File(...),
                      sura: int | None = Form(None),
                      from_: int | None = Form(None, alias="from"),
                      to: int | None = Form(None)):
    from engine.asr import transcribe
    data = await audio.read()
    if len(data) > 25 * 1024 * 1024:
        raise HTTPException(413, "Audio zu groß (max. 25 MB)")
    with tempfile.NamedTemporaryFile(suffix=os.path.splitext(audio.filename or "")[1] or ".webm") as f:
        f.write(data)
        f.flush()
        text = transcribe(f.name)
    rep = analyse(text, quran(), sura, from_, to)
    if not rep.ops:
        raise HTTPException(422, "Stelle im Quran nicht gefunden")
    return rep.to_dict()
