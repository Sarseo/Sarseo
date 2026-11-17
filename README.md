# Sarseo

Rezitations-Engine für Quran-Hifẓ: erkennt, **wo** jemand liest, und **welche Wörter** falsch, ausgelassen oder zusätzlich sind. Plan: [`docs/PLAN.md`](docs/PLAN.md).

## Phase 0: Prototyp (Python-CLI)

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m engine.cli build-db          # lädt Quran-Text (Tanzil) → data/quran.db

# Text prüfen (ohne Modell), Stelle wird automatisch gefunden
.venv/bin/python -m engine.cli check-text "قل هو الله احد الله الصمد لم يلد ولم يولد"

# Audio prüfen (lädt beim ersten Mal tarteel-ai/whisper-base-ar-quran)
.venv/bin/python -m engine.cli check aufnahme.m4a [--sura 1 --from 1 --to 7] [--json]

# Evaluierung mit EveryAyah-Aufnahmen
.venv/bin/python -m engine.cli eval --n 20 [--reciter Alafasy_128kbps]
.venv/bin/python -m pytest -q
```

### Aufbau

| Modul | Aufgabe |
|---|---|
| `engine/quran.py` | Download Tanzil-Text, SQLite-Index aller 6236 Ayat / Wörter |
| `engine/normalize.py` | Arabisch normalisieren (Tashkeel, Alif-Formen, Uthmani-Schreibweise) |
| `engine/asr.py` | Spracherkennung (Whisper, Quran-feinjustiert), ffmpeg-Dekodierung |
| `engine/align.py` | Stelle im Quran finden (n-Gramm-Voting + Fuzzy-Diff), Wort-Diff |
| `engine/report.py` | Fehlerbericht (Text / JSON für App-Anbindung) |
| `engine/evaluate.py` | WER + Trefferquote der Stellensuche |

### Erste Messung (15 zufällige Ayat, Alafasy, CPU, whisper-base)

- Wortfehlerrate: **0,5 %**
- Stelle ohne Vorgabe gefunden: **15/15**
- Laufzeit: ~5 s pro Ayah (4 CPU-Kerne, ohne Optimierung)

⚠️ Zu optimistisch: EveryAyah-Rezitatoren sind Teil der Trainingsdaten. Aussagekräftig sind erst eigene Aufnahmen (Laien, Kinder, Handy-Mikrofon).

## Quellen & Lizenzen

- Quran-Text: [Tanzil Project](https://tanzil.net) (CC BY 3.0, unverändert; wird zur Laufzeit geladen, nicht im Repo)
- Modell: [tarteel-ai/whisper-base-ar-quran](https://huggingface.co/tarteel-ai/whisper-base-ar-quran)
- Testaudio: [EveryAyah](https://everyayah.com)
