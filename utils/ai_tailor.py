"""
LLM backend for JobPilot.

Environment detection:
  - Deployed (Render, etc.): RENDER env var is set automatically by Render.
    Must have a cloud LLM key (Claude / Gemini / OpenAI). Ollama is never used.
  - Local dev: no RENDER var. Cloud keys are used if present, otherwise
    falls back to Ollama at localhost:11434.

Cloud provider priority (first key found wins):
  1. Anthropic Claude  — ANTHROPIC_API_KEY
  2. Google Gemini     — GOOGLE_API_KEY
  3. OpenAI            — OPENAI_API_KEY
"""
import json
import os
import re


_BANNED_PHRASES = """Do NOT use these words or phrases under any circumstances:
leverage, leveraging, passionate, dynamic, synergy, synergize, spearheaded, seamlessly,
robust, proactive, results-driven, detail-oriented, go-getter, thought leader,
paradigm shift, fast-paced environment, innovative solutions, game-changing, transformative,
cutting-edge, best-in-class, world-class, hit the ground running, move the needle,
circle back, take ownership, deliverables, impactful, actionable."""

_VOICE_RULES = """Writing style requirements:
- Match the natural vocabulary and tone shown in the original resume
- Vary sentence length deliberately — mix short punchy sentences (under 10 words) with longer explanatory ones (20-30 words)
- Write as if a thoughtful person typed this in one sitting, not assembled from a template
- Specific numbers and named technologies always beat vague claims
- If you cannot be specific, be brief rather than padded"""


# ── Environment & provider detection ─────────────────────────────────────────

def is_deployed() -> bool:
    """True when running on a hosted server (Render, Streamlit Cloud, etc.)."""
    return bool(
        os.getenv("RENDER")                       # Render sets this automatically
        or os.getenv("STREAMLIT_SHARING_MODE")    # Streamlit Community Cloud
        or os.getenv("ENVIRONMENT") == "production"  # generic override
    )


def get_provider() -> str:
    """Return the active LLM provider string."""
    if os.getenv("ANTHROPIC_API_KEY"):
        return "claude"
    if os.getenv("GOOGLE_API_KEY"):
        return "gemini"
    if os.getenv("OPENAI_API_KEY"):
        return "openai"
    # Only allow Ollama in local dev
    if not is_deployed():
        return "ollama"
    # Deployed with no key — caller must handle this
    return "none"


def get_provider_label() -> str:
    labels = {
        "claude": f"Claude Sonnet",
        "gemini": "Gemini 1.5 Flash",
        "openai": "GPT-4o-mini",
        "ollama": "Ollama llama3.1 (local)",
        "none": "⚠️ No LLM configured",
    }
    return labels.get(get_provider(), "Unknown")


# ── Chat dispatch ─────────────────────────────────────────────────────────────

def _chat(prompt: str, max_tokens: int = 800) -> str:
    provider = get_provider()

    if provider == "none":
        raise RuntimeError(
            "No LLM API key is configured. "
            "Set ANTHROPIC_API_KEY, GOOGLE_API_KEY, or OPENAI_API_KEY "
            "in your Render environment variables."
        )
    if provider == "claude":
        return _chat_claude(prompt, max_tokens)
    if provider == "gemini":
        return _chat_gemini(prompt, max_tokens)
    if provider == "openai":
        return _chat_openai(prompt, max_tokens)
    return _chat_ollama(prompt, max_tokens)


def _chat_claude(prompt: str, max_tokens: int) -> str:
    import anthropic
    model = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20251001")
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    msg = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.content[0].text.strip()


def _chat_gemini(prompt: str, max_tokens: int) -> str:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash")
    resp = model.generate_content(
        prompt,
        generation_config={"max_output_tokens": max_tokens},
    )
    return resp.text.strip()


def _chat_openai(prompt: str, max_tokens: int) -> str:
    from openai import OpenAI
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    msg = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.choices[0].message.content.strip()


def _chat_ollama(prompt: str, max_tokens: int) -> str:
    from openai import OpenAI
    client = OpenAI(api_key="ollama", base_url="http://localhost:11434/v1")
    msg = client.chat.completions.create(
        model="llama3.1",
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": prompt}],
    )
    return msg.choices[0].message.content.strip()


def _clean_json(raw: str) -> str:
    return re.sub(r"^```json\s*|^```\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()


# ── Public functions ──────────────────────────────────────────────────────────

def analyze_match(resume_text: str, job: dict) -> dict:
    prompt = f"""You are a recruiter screening applications. Evaluate this resume against the job posting.

RESUME:
{resume_text[:4000]}

JOB TITLE: {job['title']}
COMPANY: {job['company']}
DESCRIPTION:
{job['description'][:3000]}

Respond ONLY with raw JSON — no markdown fences, no preamble, no explanation after:
{{
  "match_score": <integer 0-100>,
  "matching_skills": ["skill1", "skill2"],
  "missing_skills": ["skill1", "skill2"],
  "strengths": ["brief point 1", "brief point 2"],
  "gaps": ["brief gap 1"],
  "summary": "<2 honest sentences, no fluff>"
}}"""

    try:
        raw = _clean_json(_chat(prompt, max_tokens=800))
        return json.loads(raw)
    except Exception:
        return {
            "match_score": 0,
            "matching_skills": [],
            "missing_skills": [],
            "strengths": [],
            "gaps": [],
            "summary": "Analysis failed. Please retry.",
        }


def tailor_resume(resume_text: str, job: dict) -> str:
    prompt = f"""You are rewriting this person's resume to target a specific role.
Your goal: produce something that passes ATS keyword scanning AND sounds like a real person wrote it — not a resume template.

ORIGINAL RESUME:
{resume_text[:5000]}

TARGET: {job['title']} at {job['company']}
JOB DESCRIPTION:
{job['description'][:3000]}

{_BANNED_PHRASES}

{_VOICE_RULES}

Structural rules:
1. Keep section order: Name/Contact → Summary → Experience → Skills → Education
2. Professional summary: 3-4 sentences, directly names this role and company, references 1-2 specific skills from the job description
3. Experience bullets: lead with the most relevant 2-3 bullets per role, de-emphasize or remove bullets unrelated to this role
4. Naturally include keywords from the job description — do not stuff them, weave them into actual sentences
5. Quantify achievements using numbers already in the original resume only. Do NOT invent metrics, companies, degrees, dates, or technologies
6. Keep ALL factual information accurate — this is non-negotiable

Output the complete tailored resume text only. No explanations before or after."""

    return _chat(prompt, max_tokens=4000)


def generate_cover_letter(resume_text: str, job: dict, candidate_name: str = "Candidate") -> str:
    company = job.get("company", "the company")
    prompt = f"""Write a cover letter for this job application. It should sound like the applicant wrote it themselves — direct, confident, and specific. Not a template.

APPLICANT RESUME:
{resume_text[:3000]}

ROLE: {job['title']} at {company}
JOB DESCRIPTION:
{job['description'][:2500]}

CANDIDATE NAME: {candidate_name}

{_BANNED_PHRASES}

{_VOICE_RULES}

Cover letter specific requirements:
- Do NOT open with "I am writing to", "I am excited to apply", "I am reaching out", or any variant of those phrases
- Open with a hook that references either: a specific thing about the company, a concrete achievement of the candidate, or a direct statement about the role — something a generic applicant could not have written
- Include exactly one genuine, specific reason to work at {company} — it must be specific enough that it would not apply to a competitor. Use what the job description reveals about the company's product, mission, or team
- Paragraph 2 and 3: Connect 2-3 concrete experiences (with numbers if available in the resume) to key requirements in the job description
- Final paragraph: Brief, direct close with a call to action. No gushing.
- Length: 3-4 paragraphs, under 380 words total
- Tone: Professional but not stiff. The way a competent person speaks, not performs.

Output only the cover letter body text. No subject line, no "Dear Hiring Manager" header, no date, no metadata."""

    return _chat(prompt, max_tokens=1200)


def suggest_job_searches(resume_text: str) -> dict:
    prompt = f"""You are a career counselor analyzing a resume to recommend job searches.

RESUME:
{resume_text[:4000]}

Based on the skills, experience level, job history, and career trajectory visible in this resume, suggest the most effective job searches this person should run.

Consider:
- What roles this person is clearly qualified for RIGHT NOW (not stretch goals)
- Alternative job titles that map to the same skills (companies use different titles for the same work)
- Whether this person is a better fit for remote, onsite, or hybrid based on their listed experience
- 3-5 concrete search queries, not generic categories

Respond ONLY with raw JSON — no markdown, no preamble:
{{
  "primary_titles": ["<most obvious job title 1>", "<title 2>"],
  "alternative_titles": ["<less obvious but valid title 1>", "<title 2>"],
  "experience_level": "<junior|mid-level|senior|staff|executive>",
  "suggested_searches": [
    {{
      "keywords": "<search keywords to enter in a job board>",
      "location_type": "<remote|onsite|hybrid|any>",
      "rationale": "<one sentence: why this search fits this resume>"
    }}
  ]
}}"""

    try:
        raw = _clean_json(_chat(prompt, max_tokens=1000))
        return json.loads(raw)
    except Exception:
        return {
            "primary_titles": [],
            "alternative_titles": [],
            "experience_level": "unknown",
            "suggested_searches": [],
        }


def generate_manual_actions(
    resume_text: str,
    job: dict,
    tailored_resume: str,
    cover_letter: str,
) -> list:
    company = job.get("company", "the company")
    prompt = f"""You are a career coach doing a final review before a job application is submitted.
Your job is to find everything the applicant needs to fix or verify manually. Be specific — generic advice is useless.

ORIGINAL RESUME (source of truth for facts):
{resume_text[:3000]}

JOB: {job['title']} at {company}

TAILORED RESUME (AI-generated, needs human review):
{tailored_resume[:4000]}

COVER LETTER (AI-generated, needs human review):
{cover_letter[:2000]}

Review for:
1. VERIFICATION — any dates, company names, job titles, or technologies in the tailored version that differ from or are absent in the original resume
2. PERSONALIZATION — any sentence in the cover letter that references {company} generically (could apply to any company). Flag the exact sentence.
3. PORTFOLIO/LINKS — if the job description mentions portfolio, GitHub, or work samples, or the candidate's original resume lists URLs that didn't make it into the tailored version
4. AUTHENTICITY — phrases that still sound like an AI template ("results-driven", "passionate about technology", "I am confident that", "I would be a great fit", "I am writing to")
5. FORMATTING — obvious structural problems (placeholder text like [Company], doubled spaces, broken bullet structure)

Return 3-8 action items (prioritize HIGH items). Respond ONLY with a raw JSON array:
[
  {{
    "priority": "<high|medium|low>",
    "category": "<verification|personalization|portfolio|authenticity|formatting>",
    "action": "<specific thing to do — name the exact text or field>",
    "reason": "<one sentence why this matters>"
  }}
]"""

    try:
        raw = _clean_json(_chat(prompt, max_tokens=1500))
        result = json.loads(raw)
        return result if isinstance(result, list) else []
    except Exception:
        return []
