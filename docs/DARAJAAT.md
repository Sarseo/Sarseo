# Anbindung an Darajaat (app.darajaat.de)

## Architektur Darajaat (Stand 2026-11-17, laut Betreiber)

| Teil | Technik |
|---|---|
| Frontend | Vanilla HTML/CSS/JS, Updates als nachgeladene Bundles (`nd65`, `nd66`, …); Hafs-Mushaf seitenweise mit Mushaf-Schriften, andere Riwayat als zeilenweise geschnittene Seitenbilder |
| Server | Node.js in Docker auf Hetzner (DE), SQLite (Konten, Fortschritt, Tests, Majalis, Rezitations-Indizes), Dateien auf Datenvolumen, Altdaten in Storage Box |
| Audio | Python + ffmpeg: Rezitation je Qāriʾ in 604 Seiten (AAC 96k) mit Ayah-Startzeiten |
| Tasmīʿ | **eigenes Wav2Vec2-CTC-Modell** (PyTorch, GPU auf RunPod), Live über WebSocket (`/api/live`): Wortverfolgung, Fehler und Ḥarakāt; langsamere Fallback-Engine; das Modell richtet auch die Qurrāʾ-Aufnahmen aus |
| Bewertung | Admin-Oberfläche `/api/admin/learn` + `/judge`: Fehlertypen miss / sub / vowel / near |
| Sonstiges | Push über ntfy; Domain bei cPanel-Anbieter → Hetzner |

## Konsequenz für Sarseo

Darajaat ist bei der Erkennung weiter als der Sarseo-Prototyp (CTC auf Zeichenebene erkennt Ḥarakāt, Whisper nicht; Live-Streaming existiert). Sarseo baut deshalb **keine zweite Erkennung**, sondern das, was fehlt:

1. **Messung:** Benchmark des Darajaat-Modells auf den bewerteten Aufnahmen (Wortfehler, Ḥaraka-Fehler, Fehlalarme pro Fehlertyp, getrennt nach Alter/Niveau). Ohne Zahlen keine gezielte Verbesserung.
2. **Datenkreislauf:** Export der `judge`-Urteile → Trainingsset → periodisches Feintuning des Wav2Vec2-Modells → Vergleich gegen festes Testset, erst dann Deployment.
3. **Funktionen aus dem Plan, die noch fehlen:** Mutashābihāt-Trainer, Spaced Repetition pro Ayah, Lehrer-/Elternberichte.
4. Die vorhandene Quran-weite Stellensuche und der Wort-Diff (`engine/align.py`) können als Prüfwerkzeug und für die Mutashābihāt dienen.

## Sarseo-Schnittstelle (Prototyp, `server/app.py`)

| Endpoint | Eingabe | Ausgabe |
|---|---|---|
| `POST /v1/check` | multipart: `audio` (webm/m4a/mp3/wav), optional `sura`, `from`, `to` | Report-JSON |
| `POST /v1/check-text` | JSON `{"text", "sura"?, "from"?, "to"?}` | Report-JSON |
| `GET /v1/health` | – | `{"ok": true}` |

Ohne `sura` findet die Engine die Stelle selbst. CORS ist für `https://app.darajaat.de` und `https://claude.ai` freigegeben (`SARSEO_ORIGINS`).

```json
{
  "span": "112:1–112:4",
  "accuracy": 0.93,
  "counts": {"ok": 14, "sub": 1, "miss": 0, "extra": 0},
  "heard": "…",
  "mistakes": [{"type": "sub", "ref": "112:4:5", "expected": "أَحَدٌ", "heard": "واحد"}]
}
```

`type` wie in Darajaat: `sub` = مبدّلة, `miss` = متروكة, `extra` = زائدة (`vowel`/`near` folgen). `ref` = Sure:Ayah:Wort.

## Aufruf aus Darajaat (Browser)

```js
const rec = new MediaRecorder(await navigator.mediaDevices.getUserMedia({audio: true}));
const chunks = []; rec.ondataavailable = e => chunks.push(e.data);
rec.onstop = async () => {
  const fd = new FormData();
  fd.append("audio", new Blob(chunks, {type: rec.mimeType}), "tilawa.webm");
  fd.append("sura", 112);
  const report = await (await fetch(SARSEO_URL + "/v1/check", {method: "POST", body: fd})).json();
  // report.accuracy, report.mistakes → Anzeige + Speicherung als Stufe
};
```

## Vorschlag: Rezitation → Darajaat-Stufen

| Stufe | Bedingung (pro Ayah-Abschnitt) |
|---|---|
| تلاوة | ≥ 90 % mit sichtbarem Text |
| حفظ | ≥ 95 % im Hifẓ-Modus (Text verdeckt) |
| إتقان | 3× ≥ 98 % an verschiedenen Tagen (Spaced Repetition) |

Fehler werden pro Wort gespeichert; der Betreuer sieht sie in seiner Ansicht und kann sie bestätigen oder verwerfen. Jede Korrektur ist zugleich Trainingsmaterial (nur mit Einwilligung).

## Offene Punkte

- **Hosting der Engine:** braucht einen Server (CPU reicht für den Start, ~4–10 s pro Ayah mit whisper-base; Echtzeit später per Streaming/GPU).
- **Darajaat als Claude-Artifact:** ob die Seite Mikrofon und externe API aufrufen darf, hängt von den Artifact-Rechten ab. Mit eigener Domain (app.darajaat.de) entfällt das.
- Der bisherige „Tilawa Trainer“ nutzt die Browser-Spracherkennung (allgemeines Arabisch). Die Sarseo-Engine ersetzt sie durch ein Quran-spezifisches Modell und prüft gegen den ganzen Quran statt nur Juzʾ ʿAmma.
