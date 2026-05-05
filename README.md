# JobPilot AI — Smart Job Application System

An AI-powered web app that searches jobs from LinkedIn, Indeed, Glassdoor and more, then tailors your resume and generates cover letters for each application.

**Live app:** https://jobpilot-latest.onrender.com

---

## Features

| Feature | Description |
|---|---|
| Job search | Pulls from Google Jobs (LinkedIn/Indeed/Glassdoor), JSearch, The Muse, RemoteOK |
| AI match scoring | Scores your resume against each job (0–100%) |
| Resume tailoring | Rewrites your resume to target the specific role |
| Cover letter | Personalized cover letter per application |
| Application tracker | Auto-tracks every application in an Excel file |

---

## Local Development

### Prerequisites

- Python 3.11+
- [Ollama](https://ollama.com) installed (for local LLM — you already have this)

### 1. Clone and install

```bash
git clone https://github.com/utsav3/jobpilot.git
cd jobpilot
pip install -r requirements.txt
```

### 2. Pull the model into Ollama

Only needed the first time:

```bash
ollama pull llama3.1
```

### 3. Start Ollama

Ollama must be running before you launch the app:

```bash
ollama serve
```

Leave this terminal open. You should see:
```
Listening on 127.0.0.1:11434
```

### 4. Set up your API keys

```bash
cp .env.example .env
```

Open `.env` and fill in any keys you want. The only required one for local dev is optional — the app works without job search API keys using The Muse and RemoteOK as free sources.

```bash
# .env
ANTHROPIC_API_KEY=        # optional locally — Ollama is used instead
SERPAPI_KEY=              # optional — Google Jobs (LinkedIn/Indeed/Glassdoor)
RAPIDAPI_KEY=             # optional — JSearch
ADZUNA_APP_ID=            # optional — Adzuna
ADZUNA_API_KEY=           # optional — Adzuna
```

### 5. Run the app

Open a second terminal (keep `ollama serve` running in the first):

```bash
streamlit run app.py
```

App opens at **http://localhost:8501**

### How the LLM is chosen locally

The app auto-detects which LLM to use:

```
Local machine
├── ANTHROPIC_API_KEY set in .env → uses Claude
├── GOOGLE_API_KEY set in .env   → uses Gemini (free)
├── OPENAI_API_KEY set in .env   → uses OpenAI
└── No cloud key                 → uses Ollama llama3.1 at localhost:11434
```

The sidebar shows which one is active (💻 Local · Ollama llama3.1).

---

## Production Deployment (Render)

The app is deployed on [Render](https://render.com) at **https://jobpilot-latest.onrender.com**.

### How it deploys

Render detects `render.yaml` in the repo and configures everything automatically:
- **Build command:** `pip install -r requirements.txt`
- **Start command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true`

On Render, the `RENDER=true` environment variable is set automatically. The app detects this and never tries to reach Ollama — it requires a cloud LLM key instead.

```
Render (deployed)
├── ANTHROPIC_API_KEY set → uses Claude   ← recommended
├── GOOGLE_API_KEY set    → uses Gemini (free)
├── OPENAI_API_KEY set    → uses OpenAI
└── No key set            → shows error, AI tab blocked
```

### Updating environment variables on Render

1. Go to [render.com](https://render.com) → your `jobpilot` service
2. Click **Environment** in the left sidebar
3. Add or edit a variable (e.g. `ANTHROPIC_API_KEY`)
4. Click **Save Changes** — Render redeploys automatically (~2 min)

### Deploying a new version

Push to `main` and Render redeploys automatically:

```bash
git add .
git commit -m "your change"
git push origin main
```

---

## API Keys Reference

### LLM (need at least one in production)

| Key | Where to get it | Cost |
|---|---|---|
| `ANTHROPIC_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | ~$1–5/month typical |
| `GOOGLE_API_KEY` | [aistudio.google.com](https://aistudio.google.com) → Get API key | Free (1M tokens/day) |
| `OPENAI_API_KEY` | [platform.openai.com](https://platform.openai.com) | ~$2–8/month typical |

### Job Search (all optional — free sources work without any key)

| Key | Where to get it | Free tier |
|---|---|---|
| `SERPAPI_KEY` | [serpapi.com](https://serpapi.com) | 100 searches/month |
| `RAPIDAPI_KEY` | rapidapi.com → search "JSearch" | 200 requests/month |
| `ADZUNA_APP_ID` + `ADZUNA_API_KEY` | [developer.adzuna.com](https://developer.adzuna.com) | 250 requests/month |

> **Note:** LinkedIn, Indeed, and Glassdoor do not offer public APIs. The best way to get jobs from them is via SerpAPI (Google Jobs) or JSearch — both aggregate those platforms.

---

## Project Structure

```
jobpilot/
├── app.py                  # Streamlit UI (all tabs)
├── utils/
│   ├── ai_tailor.py        # LLM integration (Claude / Gemini / OpenAI / Ollama)
│   ├── job_search.py       # Job search across all sources
│   ├── resume_parser.py    # PDF/DOCX text extraction
│   ├── resume_writer.py    # Generate tailored DOCX files
│   └── excel_tracker.py    # Application tracking spreadsheet
├── render.yaml             # Render deployment config
├── requirements.txt
├── .env.example
└── .gitignore
```

---

## Troubleshooting

**Ollama is not running error**
```bash
ollama serve   # start it, then refresh the app
```

**Model not found**
```bash
ollama pull llama3.1
```

**No jobs found**
- Leave the city field blank to search the whole country
- Try simpler keywords (e.g. "software engineer" not "senior python backend engineer NYC fintech")
- Free sources (The Muse, RemoteOK) have limited listings — add a SerpAPI or RapidAPI key for much better coverage

**AI tab blocked on Render**
- No LLM key is set — go to Render dashboard → Environment → add `ANTHROPIC_API_KEY` or `GOOGLE_API_KEY`

**App slow on Render free tier**
- Free tier sleeps after 15 min of inactivity and takes ~30 sec to wake up
- Upgrade to Starter ($7/month) for always-on
