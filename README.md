# NarrAI — MLH AI Hackfest

> Upload a CSV, get a natural-language insight spoken aloud — powered by Gemini 2.5 Flash + gTTS. Ask follow-up questions and get spoken answers. Upload metadata is logged to Supabase.

Live demo: [datanarrator-mlh-ai-hackfest.onrender.com](https://datanarrator-mlh-ai-hackfest.onrender.com)

---

## Architecture

```text
Browser (index.html)
   |  POST /analyze (multipart CSV)
   |  POST /followup { insight, question }
   v
FastAPI backend (main.py)
   |- supabase_agent.py    -> fire-and-forget upload logging to csv_uploads table
   |- gemini_agent.py      -> insight + chart generation (gemini-2.5-flash)
   `- tts_agent.py         -> MP3 synthesis via gTTS
```

---

## Project Structure

```text
NarrAI-MLH-AI_Hackfest/
|-- main.py
|-- index.html
|-- supabase_agent.py
|-- gemini_agent.py
|-- tts_agent.py
|-- requirements.txt
|-- render.yaml
|-- tests/
|   |-- test_main.py
|   |-- test_gemini.py
|   |-- test_tts.py
|   `-- test_supabase_agent.py
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
| Supabase project | optional — app works without it |

### Environment Variables

| Variable | Description |
|----------|-------------|
| `GEMINI_API_KEY` | Google Generative AI API key |
| `SUPABASE_URL` | Supabase project URL (optional) |
| `SUPABASE_KEY` | Supabase service-role key (optional) |

`SUPABASE_*` variables are optional. If not set, upload logging is silently skipped and all analysis still works normally.

### Running Locally

```bash
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Then open [http://localhost:8000](http://localhost:8000).

### Supabase Table Setup (optional)

If you want upload logging, run this once in your Supabase SQL editor:

```sql
create extension if not exists pgcrypto;

create table if not exists public.csv_uploads (
  id uuid primary key default gen_random_uuid(),
  session_id text not null,
  row_count integer,
  columns text[],
  created_at timestamptz default now()
);

alter table public.csv_uploads enable row level security;
```

---

## API Reference

### `GET /health`

Liveness check.

```json
{ "status": "ok" }
```

### `POST /analyze`

Upload a CSV — generates a natural-language insight, a chart, and an audio briefing.

**Request:** multipart form with `file=<csv>` (max 10MB, `.csv` only)

**Response**

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

- `chart_data` may be `null` when the dataset does not produce a meaningful chart.
- `audio_b64` may be an empty string if TTS fails.

### `POST /followup`

Ask a follow-up question about the generated insight.

**Request**

```json
{
  "insight": "Original generated insight text",
  "question": "What trend matters most here?"
}
```

**Response**

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

The repository includes a `render.yaml` blueprint.

1. Push the repo to GitHub.
2. Create a new Blueprint in [Render](https://dashboard.render.com/).
3. Set `GEMINI_API_KEY` and optionally `SUPABASE_URL` / `SUPABASE_KEY` in the Render dashboard.
4. Deploy.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) |
| AI insight + chart | [Google Gemini 2.5 Flash](https://ai.google.dev/) |
| Text-to-speech | [gTTS](https://gtts.readthedocs.io/) |
| Upload logging | [Supabase](https://www.supabase.com/) |
| Frontend | Vanilla HTML / CSS / JavaScript + Chart.js |
| Deployment | [Render](https://render.com/) |
