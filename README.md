# DataNarrator — MLH AI Hackfest

> **Query your Supabase data warehouse, generate a natural-language narrative with Google Gemini, and listen to it via ElevenLabs text-to-speech — all from a clean browser UI.**

---

## Table of Contents

- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Environment Variables](#environment-variables)
  - [Running Locally](#running-locally)
- [API Reference](#api-reference)
- [Running Tests](#running-tests)
- [Deployment (Render)](#deployment-render)
- [Tech Stack](#tech-stack)

---

## Architecture

```
Browser (HTML/CSS/JS)
       │  POST /narrate  { sql, question }
       ▼
FastAPI backend (main.py)
  ├── SupabaseAgent   → executes SQL, returns row dicts
  ├── GeminiAgent      → generates narrative from rows + question
  └── ElevenLabsAgent  → converts narrative to MP3 audio
       │  { records, narrative, audio_base64 }
       ▼
Browser renders table, narrative text, and plays audio
```

---

## Project Structure

```
dataNarrator/
├── backend/
│   ├── main.py               # FastAPI app — /health, /narrate, /query
│   ├── supabase_agent.py    # Supabase connection & SQL execution
│   ├── gemini_agent.py       # Google Gemini narrative generation
│   ├── elevenlabs_agent.py   # ElevenLabs TTS synthesis
│   ├── utils.py              # Shared helpers (env vars, table formatting)
│   └── requirements.txt      # Python dependencies
├── frontend/
│   ├── index.html            # Single-page UI
│   ├── style.css             # Dark-theme stylesheet
│   └── app.js                # Fetch API calls + DOM logic
├── tests/
│   ├── test_supabase.py     # Unit tests for SupabaseAgent
│   ├── test_gemini.py        # Unit tests for GeminiAgent
│   └── test_elevenlabs.py    # Unit tests for ElevenLabsAgent
├── .env.example              # Environment variable template
├── render.yaml               # Render.com deployment config
└── README.md
```

---

## Getting Started

### Prerequisites

| Tool | Version |
|------|---------|
| Python | ≥ 3.11 |
| pip | latest |
| Supabase account | any edition |
| Google Gemini API key | [aistudio.google.com](https://aistudio.google.com/) |
| ElevenLabs API key | [elevenlabs.io](https://elevenlabs.io/) |

### Environment Variables

Copy the example file and fill in your credentials:

```bash
cp .env.example .env
# then edit .env with your actual values
```

| Variable | Description |
|----------|-------------|
| `SUPABASE_ACCOUNT` | Supabase account identifier (e.g. `xy12345.us-east-1`) |
| `SUPABASE_USER` | Supabase username |
| `SUPABASE_PASSWORD` | Supabase password |
| `SUPABASE_WAREHOUSE` | Compute warehouse name |
| `SUPABASE_DATABASE` | Default database |
| `SUPABASE_SCHEMA` | Default schema |
| `SUPABASE_ROLE` | Optional role override |
| `GEMINI_API_KEY` | Google Generative AI API key |
| `ELEVENLABS_API_KEY` | ElevenLabs API key |
| `ELEVENLABS_VOICE_ID` | ElevenLabs voice ID to use for synthesis |

### Running Locally

```bash
# 1. Install backend dependencies
cd backend
pip install -r requirements.txt

# 2. Start the API server
uvicorn main:app --reload --port 8000

# 3. Open the frontend
#    Open frontend/index.html in your browser, or serve it:
cd ../frontend
python -m http.server 3000
#    Then visit http://localhost:3000
```

> **Note:** The frontend expects the API at `http://localhost:8000` by default.
> Override by setting `window.API_BASE` before `app.js` is loaded if you deploy
> the backend to a different URL.

---

## API Reference

### `GET /health`

Liveness check.

```json
{ "status": "ok" }
```

### `POST /narrate`

Run a SQL query, generate a narrative, and synthesize audio.

**Request body**

```json
{
  "sql":      "SELECT product, SUM(revenue) AS total FROM sales GROUP BY 1 ORDER BY 2 DESC LIMIT 5",
  "question": "What were the top 5 products by revenue?"
}
```

**Response body**

```json
{
  "records":      [ { "product": "Widget", "total": 120000 }, "..." ],
  "narrative":    "Widget was the top-performing product, generating $120 000 in revenue...",
  "audio_base64": "<base64-encoded MP3>"
}
```

### `POST /query`

Execute SQL and return raw records only (no narrative or audio).

---

## Running Tests

```bash
pip install pytest pytest-mock supabase-connector-python google-genai elevenlabs fastapi python-dotenv pydantic
pytest tests/ -v
```

---

## Deployment (Render)

The repository includes a `render.yaml` blueprint that deploys:

- **`dataNarrator-backend`** — Python web service running the FastAPI app.
- **`dataNarrator-frontend`** — Static site serving the HTML/CSS/JS files.

Steps:

1. Fork / push the repo to GitHub.
2. Create a new **Blueprint** in [Render](https://dashboard.render.com/) and point it at your repo.
3. Set the secret environment variables (API keys, Supabase credentials) in the Render dashboard.
4. Deploy!

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend API | [FastAPI](https://fastapi.tiangolo.com/) + [Uvicorn](https://www.uvicorn.org/) |
| Data warehouse | [Supabase](https://www.supabase.com/) |
| AI narrative | [Google Gemini](https://ai.google.dev/) (`gemini-1.5-flash`) |
| Text-to-speech | [ElevenLabs](https://elevenlabs.io/) (`eleven_multilingual_v2`) |
| Frontend | Vanilla HTML / CSS / JavaScript |
| Deployment | [Render](https://render.com/) |
