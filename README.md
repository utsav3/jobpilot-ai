# 🚀 JobPilot AI — Smart Job Application System

An AI-powered web app that automates your job search and application process using Claude AI.

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 Multi-resume support | Upload PDF & DOCX resumes; switch between versions |
| 🔍 Job search | Search Adzuna + JSearch (RapidAPI) simultaneously |
| 🤖 AI match analysis | Claude scores your resume against each job (0–100%) |
| ✏️ Resume tailoring | AI rewrites resume to highlight relevant skills/experience |
| 📝 Cover letter gen | Personalized cover letter for each application |
| 📊 Excel tracker | Auto-tracks every application with status, score, salary |
| 🔗 Semi-auto apply | Downloads tailored docs + opens job URL for you to submit |

---

## 🚀 Quick Start

### 1. Install dependencies

```bash
cd jobpilot
pip install -r requirements.txt
```

### 2. Set up API keys

**Option A — .env file (recommended):**
```bash
cp .env.example .env
# Edit .env and fill in your keys
```
Then load it before running:
```bash
# macOS/Linux
export $(cat .env | xargs) && streamlit run app.py

# Windows PowerShell
Get-Content .env | ForEach-Object { if ($_ -match '^([^#][^=]*)=(.*)$') { [System.Environment]::SetEnvironmentVariable($matches[1].Trim(), $matches[2].Trim()) } }
streamlit run app.py
```

**Option B — Enter keys in the app sidebar** (no file needed, keys last for the session).

### 3. Run the app

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**

---

## 🔑 API Keys Setup

### Anthropic API Key (Required)
- Go to [console.anthropic.com](https://console.anthropic.com)
- Create an account and generate an API key
- Costs: ~$0.003–0.015 per resume tailoring + cover letter (Claude Sonnet)

### Adzuna API (Free — Recommended)
- Register at [developer.adzuna.com](https://developer.adzuna.com)
- Free tier: 250 requests/month
- You get an **App ID** and **API Key**

### JSearch via RapidAPI (Free tier available)
- Sign up at [RapidAPI](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)
- Subscribe to JSearch (free tier: 200 requests/month)
- Copy your **RapidAPI Key** from the dashboard

> **Note:** You need at least one job search API key. If you have both, results are combined and deduplicated.

---

## 📖 How to Use

### Step 1 — Upload Resumes
1. Go to the **📄 Resumes** tab
2. Upload one or more PDF/DOCX resumes
3. Set one as "Active" (this is the base the AI will tailor)

### Step 2 — Search Jobs
1. Go to the **🔍 Job Search** tab
2. Enter keywords (e.g. "Software Engineer") and location
3. Use filters for remote, salary range
4. Click **+ Select** on jobs you want to apply to

### Step 3 — AI Apply
1. Go to the **🤖 AI Apply** tab
2. Choose whether to generate cover letters
3. Click **⚡ Process All Selected Jobs**
4. For each job, the AI will:
   - Score the match (0–100%)
   - Identify matching and missing skills
   - Tailor your resume
   - Write a cover letter
5. Download the tailored resume + cover letter
6. Click "Open Job Posting" to apply manually

### Step 4 — Track Applications
1. Go to the **📊 Tracker** tab
2. View all applications with match scores, salary, status
3. Filter and sort by status, company, date
4. Download the full Excel tracker

---

## 📁 Project Structure

```
jobpilot/
├── app.py                    # Main Streamlit app
├── utils/
│   ├── resume_parser.py      # PDF/DOCX text extraction
│   ├── job_search.py         # Adzuna + JSearch APIs
│   ├── ai_tailor.py          # Claude AI integration
│   ├── excel_tracker.py      # Application tracking
│   └── resume_writer.py      # Generate tailored DOCX files
├── requirements.txt
├── .env.example
└── README.md
```

---

## ⚠️ Important Notes

- **Do not fabricate experience**: The AI is instructed to only use information from your actual resume. Always review before submitting.
- **API costs**: Each job processed uses ~2–3 Claude API calls. At current Sonnet pricing, expect ~$0.01–0.05 per job.
- **Job site ToS**: This tool searches official APIs and opens job URLs for you to submit manually. It does not scrape or auto-submit forms, respecting job site terms of service.
- **Resume quality**: The better your original resume, the better the tailored output.

---

## 🛠️ Troubleshooting

**No jobs found?**
- Check your API keys are saved (click "Save Keys" in sidebar)
- Try broader keywords or different location
- Ensure at least one job search API key is set

**AI processing fails?**
- Verify your Anthropic API key has credits
- Check the key is saved via the sidebar

**DOCX won't open?**
- Ensure Microsoft Word or LibreOffice is installed
- Try re-downloading the file

---

## 🔮 Future Improvements

- [ ] LinkedIn Easy Apply integration
- [ ] Indeed one-click apply
- [ ] Email follow-up drafts
- [ ] Interview prep Q&A per job
- [ ] Application analytics dashboard
