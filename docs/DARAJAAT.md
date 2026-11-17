# Anbindung an Darajaat (app.darajaat.de)

Darajaat ist eine arabische Lernplattform (Ansichten: Schüler / Betreuer / wissenschaftlicher Prüfer; Quiz, Zertifikate). Sarseo liefert ihr ein **Tilāwa-/Hifẓ-Modul**: Rezitation prüfen, Fehler pro Wort, Fortschritt als Darajaat-Stufen.

## Schnittstelle (fertig, `server/app.py`)

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
  "counts": {"ok": 14, "sub": 1, "del": 0, "ins": 0},
  "heard": "…",
  "mistakes": [{"type": "sub", "ref": "112:4:5", "expected": "أَحَدٌ", "heard": "واحد"}]
}
```

`type`: `sub` = falsches Wort, `del` = ausgelassen, `ins` = zusätzlich. `ref` = Sure:Ayah:Wort.

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
