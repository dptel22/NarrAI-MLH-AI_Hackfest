# DataNarrator - MLH AI Hackfest

> Upload a CSV, optionally log it to Supabase, generate a natural-language insight with Google Gemini, and listen to it with ElevenLabs from a simple browser UI.

---

## Architecture

```text
Browser (index.html)
   |  POST /analyze (multipart CSV)
   |  POST /followup { insight, question }
   v
FastAPI backend (main.py)
   |- supabase_agent.py    -> optional CSV row ingestion
   |- gemini_agent.py      -> insight + chart generation
   `- elevenlabs_agent.py  -> MP3 synthesis
```

---

## Project Structure

```text
DataNarrator--MLH-AI-Hackfest/
|-- main.py
|-- index.html
|-- supabase_agent.py
|-- gemini_agent.py
|-- elevenlabs_agent.py
|-- requirements.txt
|-- render.yaml
|-- tests/
|   |-- test_main.py
|   |-- test_gemini.py
|   `-- test_elevenlabs.py
`-- README.md
```

---

## Getting Started

### Prerequisites

| Tool | Version |
|------|---------|
| Python | >= 3.11 |
| pip | latest |
| Google Gemini API key | [aistudio.google.com](https://aistudio.google.com/) |
| ElevenLabs API key | [elevenlabs.io](https://elevenlabs.io/) |
| Supabase project | optional |

### Environment Variables

Copy the example file and fill in your credentials:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `SUPABASE_URL` | Supabase project URL |
| `SUPABASE_KEY` | Supabase key with insert access |
| `GEMINI_API_KEY` | Google Generative AI API key |
| `ELEVENLABS_API_KEY` | ElevenLabs API key |
| `ELEVENLABS_VOICE_ID` | ElevenLabs voice ID used for synthesis |

`SUPABASE_*` variables are optional; the app still analyzes CSVs locally if Supabase is not configured.

### Running Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Then open [http://localhost:8000](http://localhost:8000).

---

## API Reference

### `GET /health`

Liveness check.

```json
{ "status": "ok" }
```

### `POST /analyze`

Upload a CSV, summarize it, generate an insight, and optionally generate chart/audio output.

**Request**

- Multipart form upload with `file=<csv>`

**Response body**

```json
{
  "insight": "Three sentence narrative ending with one actionable recommendation.",
  "chart_data": {
    "type": "bar",
    "labels": ["A", "B", "C"],
    "values": [10, 8, 4],
    "title": "Top Categories"
  },
  "audio_b64": "<base64-encoded MP3>",
  "table_name": "upload_ab12cd34",
  "row_count": 123,
  "columns": ["category", "value"]
}
```

Notes:

- `chart_data` may be `null` when the dataset does not produce a meaningful chart.
- `audio_b64` may be an empty string if TTS is unavailable or intentionally skipped.
- Column information is returned as `columns`, not `col_count`.

### `POST /followup`

Ask a follow-up question about the generated insight.

**Request body**

```json
{
  "insight": "Original generated insight text",
  "question": "What trend matters most here?"
}
```

**Response body**

```json
{
  "answer": "Short follow-up answer.",
  "audio_b64": "<base64-encoded MP3>"
}
```

---

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```

---

## Deployment (Render)

The repository includes a `render.yaml` blueprint for deploying the FastAPI backend to Render.

Steps:

1. Push the repo to GitHub.
2. Create a new Blueprint in [Render](https://dashboard.render.com/).
3. Set the required API keys and any optional Supabase credentials in the Render dashboard.
4. Deploy.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) |
| Storage | [Supabase](https://www.supabase.com/) |
| AI insight | [Google Gemini](https://ai.google.dev/) |
| Text-to-speech | [ElevenLabs](https://elevenlabs.io/) |
| Frontend | Vanilla HTML / CSS / JavaScript |
| Deployment | [Render](https://render.com/) |
