"""
JobPilot AI — Smart Job Application System
Run: streamlit run app.py
"""
import os
import tempfile
from datetime import datetime

import streamlit as st

st.set_page_config(
    page_title="JobPilot AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Design system ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

/* ── Brand colours ── */
:root {
  --primary:       #6366f1;
  --primary-dark:  #4f46e5;
  --primary-light: #eef2ff;
  --success:       #10b981;
  --success-light: #d1fae5;
  --warning:       #f59e0b;
  --warning-light: #fef3c7;
  --danger:        #ef4444;
  --danger-light:  #fee2e2;
  --muted:         #64748b;
  --border:        #e2e8f0;
  --surface:       #f8fafc;
  --card:          #ffffff;
}

/* ── Global tweaks ── */
.block-container { padding-top: 1.5rem !important; }
h1, h2, h3 { letter-spacing: -0.3px; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1e1b4b 0%, #312e81 100%) !important;
}
[data-testid="stSidebar"] * { color: #e0e7ff !important; }
[data-testid="stSidebar"] .stMetric label { color: #a5b4fc !important; }
[data-testid="stSidebar"] .stMetric [data-testid="stMetricValue"] {
    color: #ffffff !important; font-size: 1.4rem !important;
}
[data-testid="stSidebar"] hr { border-color: #4338ca !important; opacity: 0.4; }

/* Step rows in sidebar */
.step-row {
    display: flex; align-items: center; gap: 10px;
    padding: 6px 0; font-size: 0.88rem;
}
.step-num {
    width: 24px; height: 24px; border-radius: 50%; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.72rem; font-weight: 700;
    background: rgba(255,255,255,0.15); color: #c7d2fe;
}
.step-done .step-num { background: #10b981; color: white; }
.step-active .step-num { background: #6366f1; color: white; }
.step-label { line-height: 1.2; }
.step-done .step-label { color: #a7f3d0 !important; }
.step-active .step-label { color: #ffffff !important; font-weight: 600; }

/* ── Hero banner (welcome screen) ── */
.hero {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #06b6d4 100%);
    border-radius: 16px; padding: 2.5rem 2rem;
    color: white; text-align: center; margin-bottom: 1.5rem;
}
.hero h1 { font-size: 2.2rem; font-weight: 700; margin: 0 0 0.4rem; color: white !important; }
.hero p  { font-size: 1.05rem; opacity: 0.9; margin: 0 0 1.5rem; }
.hero-pills { display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; margin-top: 1rem; }
.hero-pill {
    background: rgba(255,255,255,0.2); backdrop-filter: blur(4px);
    border-radius: 20px; padding: 5px 14px; font-size: 0.82rem; font-weight: 500;
}

/* ── Job cards ── */
.jcard {
    background: var(--card); border-radius: 12px;
    border: 1.5px solid var(--border);
    padding: 1rem 1.2rem; margin-bottom: 0.75rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    transition: box-shadow 0.15s, border-color 0.15s;
}
.jcard:hover { box-shadow: 0 4px 12px rgba(99,102,241,0.12); border-color: #c7d2fe; }
.jcard.selected { border-color: var(--primary) !important; background: var(--primary-light); }

.jcard-title { font-size: 0.98rem; font-weight: 600; color: #1e293b; margin-bottom: 2px; }
.jcard-company { font-size: 0.88rem; color: var(--muted); }
.jcard-meta { display: flex; gap: 12px; flex-wrap: wrap; margin-top: 6px; font-size: 0.78rem; color: var(--muted); }
.jcard-meta span { display: flex; align-items: center; gap: 3px; }

/* Source badges */
.badge {
    display: inline-block; padding: 2px 8px; border-radius: 10px;
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.2px;
}
.badge-linkedin  { background: #dbeafe; color: #1d4ed8; }
.badge-indeed    { background: #fce7f3; color: #9d174d; }
.badge-glassdoor { background: #d1fae5; color: #065f46; }
.badge-google    { background: #fef3c7; color: #92400e; }
.badge-muse      { background: #ede9fe; color: #5b21b6; }
.badge-remoteok  { background: #f0fdf4; color: #14532d; }
.badge-manual    { background: #f1f5f9; color: #475569; }
.badge-default   { background: #f1f5f9; color: #475569; }

/* Score ring */
.score-ring {
    width: 72px; height: 72px; border-radius: 50%; border: 5px solid;
    display: flex; align-items: center; justify-content: center;
    font-size: 1.1rem; font-weight: 700; margin: 0 auto;
}
.ring-high   { border-color: var(--success); color: var(--success); }
.ring-medium { border-color: var(--warning); color: var(--warning); }
.ring-low    { border-color: var(--danger);  color: var(--danger);  }

/* Skill chips */
.chip {
    display: inline-block; padding: 2px 9px; border-radius: 8px;
    font-size: 0.73rem; margin: 2px; font-weight: 500;
}
.chip-good    { background: var(--success-light); color: #065f46; }
.chip-missing { background: var(--warning-light); color: #78350f; }

/* Stat boxes */
.stat-box {
    background: var(--card); border-radius: 10px; padding: 1rem;
    border: 1px solid var(--border); text-align: center;
}
.stat-num   { font-size: 1.9rem; font-weight: 700; }
.stat-label { font-size: 0.75rem; color: var(--muted); margin-top: 2px; }

/* Action item rows */
.action-row {
    display: flex; gap: 10px; padding: 8px 0;
    border-bottom: 1px solid var(--border); align-items: flex-start;
}
.action-row:last-child { border-bottom: none; }

/* Upload zone hint */
.upload-hint {
    background: var(--primary-light); border: 2px dashed #a5b4fc;
    border-radius: 12px; padding: 2rem; text-align: center; color: var(--primary);
}

/* Info strip */
.info-strip {
    background: var(--primary-light); border-left: 4px solid var(--primary);
    border-radius: 0 8px 8px 0; padding: 0.7rem 1rem;
    font-size: 0.88rem; color: #3730a3; margin-bottom: 1rem;
}

/* CTA banner */
.cta-banner {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    border-radius: 10px; padding: 0.9rem 1.2rem;
    color: white; display: flex; align-items: center;
    justify-content: space-between; gap: 1rem; margin: 1rem 0;
}
</style>
""", unsafe_allow_html=True)


# ── Session state ─────────────────────────────────────────────────────────────
def _init():
    defaults = {
        "resumes": [],
        "active_resume_idx": 0,
        "jobs": [],
        "selected_jobs": set(),
        "results": {},
        "tmp_dir": tempfile.mkdtemp(prefix="jobpilot_"),
        "job_suggestions": None,
        "search_prefill": {},
        "candidate_name": "",
        "last_search": {},
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()

# ── Helpers ───────────────────────────────────────────────────────────────────
def _source_badge(source: str) -> str:
    s = source.lower()
    if "linkedin"  in s: cls, label = "badge-linkedin",  "LinkedIn"
    elif "indeed"  in s: cls, label = "badge-indeed",   "Indeed"
    elif "glassdoor" in s: cls, label = "badge-glassdoor", "Glassdoor"
    elif "google"  in s: cls, label = "badge-google",   "Google Jobs"
    elif "muse"    in s: cls, label = "badge-muse",     "The Muse"
    elif "remoteok" in s: cls, label = "badge-remoteok", "RemoteOK"
    elif "manual"  in s: cls, label = "badge-manual",   "Manual"
    else:                 cls, label = "badge-default",  source.split("(")[0].strip()
    return f'<span class="badge {cls}">{label}</span>'

def _score_class(score):
    if score >= 75: return "ring-high"
    if score >= 50: return "ring-medium"
    return "ring-low"

def _active_step():
    if not st.session_state.resumes:           return 1
    if not st.session_state.jobs:              return 2
    if not st.session_state.selected_jobs:     return 3
    return 4


# ════════════════════════════════════════════════════════════════════════════
# SIDEBAR
# ════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🚀 JobPilot AI")
    st.caption("AI-powered job applications")
    st.divider()

    # Workflow progress
    st.markdown("**Your progress**")
    step = _active_step()
    steps = [
        ("Upload your resume",    len(st.session_state.resumes) > 0),
        ("Search for jobs",       len(st.session_state.jobs) > 0),
        ("Select jobs to apply",  len(st.session_state.selected_jobs) > 0),
        ("Generate & apply",      len(st.session_state.results) > 0),
    ]
    for i, (label, done) in enumerate(steps, 1):
        is_active = (i == step)
        row_cls = "step-row step-done" if done else ("step-row step-active" if is_active else "step-row")
        num_html = "✓" if done else str(i)
        st.markdown(
            f'<div class="{row_cls}">'
            f'<div class="step-num">{num_html}</div>'
            f'<div class="step-label">{label}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # Stats
    r = len(st.session_state.resumes)
    j = len(st.session_state.jobs)
    s = len(st.session_state.selected_jobs)
    p = len(st.session_state.results)
    c1, c2 = st.columns(2)
    with c1:
        st.metric("Resumes", r)
        st.metric("Selected", s)
    with c2:
        st.metric("Jobs Found", j)
        st.metric("Processed", p)

    st.divider()

    # AI engine status — no user-facing key input
    from utils.ai_tailor import get_provider, get_provider_label, is_deployed
    provider = get_provider()
    label    = get_provider_label()
    if provider == "none":
        st.error("⚠️ AI not configured")
    else:
        st.success(f"✦ Powered by **{label}**")
        if provider == "ollama":
            st.caption("Running locally · upgrade to cloud for best results")

    st.divider()
    st.caption("JobPilot AI · v2.0")


# ════════════════════════════════════════════════════════════════════════════
# TABS
# ════════════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs([
    "📄  Resume",
    "🔍  Find Jobs",
    "⚡  AI Apply",
    "📊  Tracker",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — RESUME
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    has_resumes = bool(st.session_state.resumes)

    if not has_resumes:
        # Welcome hero
        st.markdown("""
        <div class="hero">
          <h1>Welcome to JobPilot AI</h1>
          <p>Upload your resume and let AI find, match, and tailor applications for you — in minutes.</p>
          <div class="hero-pills">
            <span class="hero-pill">🔍 Searches LinkedIn &amp; Indeed</span>
            <span class="hero-pill">🤖 Powered by Claude Sonnet</span>
            <span class="hero-pill">📄 Tailored resume per job</span>
            <span class="hero-pill">📝 Cover letter included</span>
          </div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("### Start here — upload your resume")
        st.caption("PDF or DOCX · your file stays private and is never stored on our servers")
    else:
        st.markdown("## 📄 Your Resume")
        active = st.session_state.resumes[st.session_state.active_resume_idx]
        st.markdown(
            f'<div class="info-strip">Active resume: <strong>{active["display_name"]}</strong> · '
            f'~{len(active["raw_text"].split())} words · {active["format"].upper()}</div>',
            unsafe_allow_html=True,
        )

    uploaded = st.file_uploader(
        "Upload resume",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed",
        help="Upload PDF or DOCX",
    )

    if uploaded:
        from utils.resume_parser import parse_resume
        existing = {r["name"] for r in st.session_state.resumes}
        added = 0
        for f in uploaded:
            if f.name in existing:
                continue
            path = os.path.join(st.session_state.tmp_dir, f.name)
            with open(path, "wb") as fp:
                fp.write(f.read())
            try:
                parsed = parse_resume(path)
                parsed["display_name"] = f.name
                st.session_state.resumes.append(parsed)
                added += 1
                existing.add(f.name)
            except Exception as e:
                st.error(f"Could not read {f.name}: {e}")
        if added:
            st.success(f"✅ {added} resume(s) uploaded. Head to **Find Jobs** to get started.")
            st.rerun()

    if st.session_state.resumes:
        st.markdown("---")
        for i, resume in enumerate(st.session_state.resumes):
            is_active = st.session_state.active_resume_idx == i
            border = "border: 2px solid #6366f1;" if is_active else ""
            with st.container():
                st.markdown(f'<div class="jcard" style="{border}">', unsafe_allow_html=True)
                ca, cb, cc = st.columns([6, 2, 2])
                with ca:
                    badge_html = '<span style="color:#6366f1;font-size:0.75rem;font-weight:600">● ACTIVE</span>' if is_active else '<span style="color:#94a3b8;font-size:0.75rem">○ inactive</span>'
                    st.markdown(f"**{resume['display_name']}** &nbsp; {badge_html}", unsafe_allow_html=True)
                    st.caption(resume["raw_text"][:160].replace("\n", " ") + "…")
                with cb:
                    st.caption(f"`{resume['format'].upper()}` · {len(resume['raw_text'].split())} words")
                with cc:
                    if not is_active and st.button("Set active", key=f"act_{i}", use_container_width=True):
                        st.session_state.active_resume_idx = i
                        st.rerun()
                    if st.button("Remove", key=f"rm_{i}", use_container_width=True):
                        st.session_state.resumes.pop(i)
                        st.session_state.active_resume_idx = max(0, st.session_state.active_resume_idx - 1)
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        with st.expander("👁️ Preview resume text"):
            st.text_area(
                "", st.session_state.resumes[st.session_state.active_resume_idx]["raw_text"],
                height=380, label_visibility="collapsed",
            )

        # CTA to next step
        st.markdown(
            '<div class="cta-banner">'
            '<span>Resume ready — now find jobs that fit your profile</span>'
            '</div>',
            unsafe_allow_html=True,
        )


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — JOB SEARCH
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 🔍 Find Jobs")

    if not st.session_state.resumes:
        st.info("⬅️ Upload your resume first so AI can recommend the right searches for you.")

    # ── AI recommendations ────────────────────────────────────────────────
    if st.session_state.resumes:
        with st.container():
            col_hd, col_btn = st.columns([4, 2])
            with col_hd:
                st.markdown("### 🎯 AI Job Recommendations")
                st.caption("Claude analyses your resume and suggests the best searches for you")
            with col_btn:
                st.markdown("<div style='margin-top:1rem'>", unsafe_allow_html=True)
                recommend_btn = st.button("✨ Recommend jobs for me", type="primary", use_container_width=True)
                st.markdown("</div>", unsafe_allow_html=True)

        if recommend_btn:
            from utils.ai_tailor import suggest_job_searches
            active_r = st.session_state.resumes[st.session_state.active_resume_idx]
            with st.spinner("Analysing your resume with Claude Sonnet…"):
                st.session_state.job_suggestions = suggest_job_searches(active_r["raw_text"])
                st.session_state.search_prefill = {}
            st.rerun()

        if st.session_state.job_suggestions:
            sugg = st.session_state.job_suggestions
            exp = sugg.get("experience_level", "")
            titles = sugg.get("primary_titles", []) + sugg.get("alternative_titles", [])

            if exp and exp != "unknown":
                st.markdown(
                    f'<div class="info-strip">Claude detected you as <strong>{exp}</strong> · '
                    f'suggested titles: {", ".join(f"<strong>{t}</strong>" for t in titles[:4])}</div>',
                    unsafe_allow_html=True,
                )

            cols = st.columns(min(len(sugg.get("suggested_searches", [])), 3))
            for i, s in enumerate(sugg.get("suggested_searches", [])[:3]):
                loc_icon = {"remote": "🌐", "onsite": "🏢", "hybrid": "🔄"}.get(s.get("location_type", ""), "📍")
                with cols[i]:
                    st.markdown(
                        f'<div class="jcard">'
                        f'<div class="jcard-title">{loc_icon} {s["keywords"]}</div>'
                        f'<div class="jcard-company" style="margin-top:4px">{s.get("rationale","")}</div>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    if st.button("Search this →", key=f"sugg_{i}", use_container_width=True):
                        st.session_state.search_prefill = {
                            "keywords": s["keywords"],
                            "location": "Remote" if s.get("location_type") == "remote" else "",
                        }
                        st.rerun()

            if st.button("✕ Clear recommendations", type="secondary"):
                st.session_state.job_suggestions = None
                st.session_state.search_prefill = {}
                st.rerun()

        st.markdown("---")

    # ── Search form ───────────────────────────────────────────────────────
    with st.form("search_form", clear_on_submit=False):
        st.markdown("### Search")
        fc1, fc2, fc3 = st.columns([4, 3, 1])
        with fc1:
            keywords = st.text_input(
                "Job title or keywords",
                value=st.session_state.search_prefill.get("keywords", ""),
                placeholder="e.g. Software Engineer, Data Analyst",
            )
        with fc2:
            country = st.selectbox(
                "Country",
                ["United States", "United Kingdom", "Canada", "Australia", "Germany"],
            )
        with fc3:
            num_results = st.number_input("Results", 5, 50, 20, label_visibility="visible")

        location = st.text_input(
            "City or state (optional — leave blank for nationwide)",
            value=st.session_state.search_prefill.get("location", ""),
            placeholder="e.g. New York · Austin, TX · Remote",
        )

        ff1, ff2 = st.columns(2)
        with ff1:
            remote_only = st.checkbox("Remote jobs only")
        with ff2:
            min_salary = st.number_input("Min. salary (USD)", 0, 500_000, 0, step=10_000)

        search_btn = st.form_submit_button("🔍 Search jobs", use_container_width=True, type="primary")

    if search_btn:
        st.session_state.search_prefill = {}
        if not keywords.strip():
            st.warning("Enter a job title or keywords to search.")
        else:
            from utils.job_search import search_jobs
            loc_display = f"{location.strip()}, {country}" if location.strip() else country
            with st.spinner(f"Searching {loc_display}…"):
                jobs = search_jobs(keywords.strip(), location.strip(), country=country, num=num_results)
            if remote_only:
                jobs = [j for j in jobs if j.get("remote") or "remote" in (j.get("location", "") + j.get("title", "")).lower()]
            if min_salary > 0:
                jobs = [j for j in jobs if (j.get("salary_min") or 0) >= min_salary or (j.get("salary_max") or 0) >= min_salary]
            st.session_state.jobs = jobs
            st.session_state.selected_jobs = set()
            st.session_state.last_search = {"keywords": keywords, "location": loc_display}
            if not jobs:
                st.warning("No jobs found. Try simpler keywords or leave the city field blank.")

    # ── Manual paste ──────────────────────────────────────────────────────
    with st.expander("📋 Paste a job from LinkedIn / Indeed manually"):
        st.caption("Found a job you like? Paste the details here and it'll be added to your list.")
        with st.form("manual_form"):
            mc1, mc2 = st.columns(2)
            with mc1:
                mj_title   = st.text_input("Job title *", placeholder="Senior Software Engineer")
                mj_company = st.text_input("Company *",   placeholder="Acme Corp")
            with mc2:
                mj_loc = st.text_input("Location", placeholder="New York, NY or Remote")
                mj_url = st.text_input("Job URL",  placeholder="https://linkedin.com/jobs/…")
            mj_desc = st.text_area("Job description *", placeholder="Paste the full job description…", height=160)
            add_btn = st.form_submit_button("➕ Add to list", type="primary")

        if add_btn:
            if not mj_title or not mj_company or not mj_desc:
                st.error("Title, company and description are required.")
            else:
                manual = {
                    "title": mj_title.strip(), "company": mj_company.strip(),
                    "location": mj_loc.strip() or "Not specified",
                    "description": mj_desc.strip(), "url": mj_url.strip(),
                    "salary_min": None, "salary_max": None,
                    "salary_display": "Not specified",
                    "posted_date": "", "source": "Manual", "employment_type": "",
                    "remote": "remote" in mj_loc.lower(),
                }
                key = (manual["title"].lower(), manual["company"].lower())
                existing_keys = {(j["title"].lower(), j["company"].lower()) for j in st.session_state.jobs}
                if key in existing_keys:
                    st.warning("Already in your list.")
                else:
                    st.session_state.jobs.append(manual)
                    st.success(f"✅ Added **{mj_title}** at **{mj_company}**.")
                    st.rerun()

    # ── Job results ───────────────────────────────────────────────────────
    if st.session_state.jobs:
        st.markdown("---")
        hdr1, hdr2, hdr3 = st.columns([4, 1, 1])
        with hdr1:
            search_info = st.session_state.last_search
            title_str = f'"{search_info.get("keywords", "")}" in {search_info.get("location", "")}' if search_info else ""
            st.markdown(f"### {len(st.session_state.jobs)} jobs found {title_str}")
        with hdr2:
            if st.button("Select all", use_container_width=True):
                st.session_state.selected_jobs = set(range(len(st.session_state.jobs)))
                st.rerun()
        with hdr3:
            if st.button("Clear all", use_container_width=True):
                st.session_state.selected_jobs = set()
                st.rerun()

        for idx, job in enumerate(st.session_state.jobs):
            selected = idx in st.session_state.selected_jobs
            card_cls = "jcard selected" if selected else "jcard"

            salary = job.get("salary_display", "")
            salary_str = f"💰 {salary}" if salary and salary != "Not specified" else ""
            emp_str = f"🕐 {job['employment_type']}" if job.get("employment_type") else ""
            remote_str = "🌐 Remote" if job.get("remote") else ""
            date_str = f"📅 {job['posted_date']}" if job.get("posted_date") else ""

            meta_parts = [p for p in [f"📍 {job['location']}", salary_str, emp_str, remote_str, date_str] if p]
            badge_html = _source_badge(job.get("source", ""))

            with st.container():
                st.markdown(f'<div class="{card_cls}">', unsafe_allow_html=True)
                col_info, col_action = st.columns([7, 2])
                with col_info:
                    st.markdown(
                        f'<div class="jcard-title">{job["title"]} &nbsp;{badge_html}</div>'
                        f'<div class="jcard-company">{job["company"]}</div>'
                        f'<div class="jcard-meta">{"  ·  ".join(meta_parts)}</div>',
                        unsafe_allow_html=True,
                    )
                with col_action:
                    btn_label = "✅ Selected" if selected else "+ Select"
                    btn_type  = "primary" if selected else "secondary"
                    if st.button(btn_label, key=f"sel_{idx}", use_container_width=True, type=btn_type):
                        if selected:
                            st.session_state.selected_jobs.discard(idx)
                        else:
                            st.session_state.selected_jobs.add(idx)
                        st.rerun()

                with st.expander("View description"):
                    desc = job.get("description", "No description available.")
                    st.write(desc[:2000] + ("…" if len(desc) > 2000 else ""))
                    if job.get("url"):
                        st.link_button("Open original posting ↗", job["url"])

                st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.selected_jobs:
            n = len(st.session_state.selected_jobs)
            st.markdown(
                f'<div class="cta-banner">'
                f'<span><strong>{n} job{"s" if n > 1 else ""} selected</strong> — '
                f'go to ⚡ AI Apply to generate your tailored resume and cover letter</span>'
                f'</div>',
                unsafe_allow_html=True,
            )


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — AI APPLY
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## ⚡ AI Apply")

    # Guard: resume
    if not st.session_state.resumes:
        st.markdown(
            '<div class="upload-hint">'
            '<h3 style="margin:0 0 0.5rem">No resume uploaded yet</h3>'
            '<p style="margin:0">Go to the <strong>📄 Resume</strong> tab and upload your resume first.</p>'
            '</div>', unsafe_allow_html=True,
        )
        st.stop()

    # Guard: jobs selected
    if not st.session_state.selected_jobs:
        st.markdown(
            '<div class="upload-hint">'
            '<h3 style="margin:0 0 0.5rem">No jobs selected</h3>'
            '<p style="margin:0">Go to <strong>🔍 Find Jobs</strong>, search for roles, and click <em>+ Select</em> on the ones you want to apply to.</p>'
            '</div>', unsafe_allow_html=True,
        )
        st.stop()

    # Guard: LLM
    from utils.ai_tailor import get_provider, get_provider_label, is_deployed
    provider = get_provider()
    if provider == "none":
        st.error("AI is not configured. Contact support or set up an LLM API key on the server.")
        st.stop()
    if provider == "ollama":
        import urllib.request
        try:
            urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        except Exception:
            st.warning("Ollama isn't running. Run `ollama serve` in your terminal, then refresh.")
            st.stop()

    active_resume  = st.session_state.resumes[st.session_state.active_resume_idx]
    sel_indices    = sorted(st.session_state.selected_jobs)
    sel_jobs       = [st.session_state.jobs[i] for i in sel_indices]

    from utils.resume_parser import extract_name_from_resume
    candidate_name = extract_name_from_resume(active_resume["raw_text"])
    st.session_state.candidate_name = candidate_name

    # Summary strip
    st.markdown(
        f'<div class="info-strip">'
        f'Resume: <strong>{active_resume["display_name"]}</strong> &nbsp;·&nbsp; '
        f'<strong>{len(sel_jobs)}</strong> job{"s" if len(sel_jobs) > 1 else ""} selected &nbsp;·&nbsp; '
        f'AI: <strong>{get_provider_label()}</strong>'
        f'</div>',
        unsafe_allow_html=True,
    )

    # Options row
    opt1, opt2 = st.columns(2)
    with opt1:
        gen_cover  = st.checkbox("Generate cover letter for each job", value=True)
    with opt2:
        auto_track = st.checkbox("Auto-add to application tracker", value=True)

    # Process button
    if st.button("⚡ Generate applications for all selected jobs", type="primary", use_container_width=True):
        from utils.ai_tailor import analyze_match, tailor_resume, generate_cover_letter, generate_manual_actions
        from utils.excel_tracker import add_application
        from utils.resume_writer import create_tailored_docx, create_cover_letter_docx

        bar    = st.progress(0)
        status = st.empty()

        for i, (orig_idx, job) in enumerate(zip(sel_indices, sel_jobs)):
            bar.progress(int(i / len(sel_jobs) * 100), text=f"Processing {i+1}/{len(sel_jobs)}: {job['title']} at {job['company']}")
            try:
                status.caption("🔍 Scoring match…")
                match = analyze_match(active_resume["raw_text"], job)

                status.caption("✏️ Tailoring resume…")
                tailored = tailor_resume(active_resume["raw_text"], job)

                cover = ""
                if gen_cover:
                    status.caption("📝 Writing cover letter…")
                    cover = generate_cover_letter(active_resume["raw_text"], job, candidate_name)

                actions = []
                try:
                    status.caption("📋 Generating action checklist…")
                    actions = generate_manual_actions(active_resume["raw_text"], job, tailored, cover)
                except Exception:
                    pass

                safe = lambda s: "".join(c for c in s if c.isalnum() or c in " -_")[:28].strip()
                base = f"{safe(job['company'])}_{safe(job['title'])}".replace(" ", "_")

                r_path = os.path.join(st.session_state.tmp_dir, f"Resume_{base}.docx")
                create_tailored_docx(tailored, job, r_path, candidate_name)

                c_path = ""
                if gen_cover and cover:
                    c_path = os.path.join(st.session_state.tmp_dir, f"Cover_{base}.docx")
                    create_cover_letter_docx(cover, job, c_path, candidate_name)

                if auto_track:
                    add_application(job, match.get("match_score", 0), active_resume["display_name"], has_cover_letter=bool(cover))

                st.session_state.results[orig_idx] = {
                    "match": match, "tailored_text": tailored,
                    "cover_text": cover, "resume_path": r_path, "cover_path": c_path,
                    "job": job, "manual_actions": actions,
                    "edited_resume": None, "edited_cover": None,
                }
            except Exception as e:
                st.error(f"Error on {job['title']}: {e}")

        bar.progress(100, text="✅ Done!")
        status.empty()
        st.success(f"🎉 Generated applications for {len(sel_jobs)} job(s). Review and download below.")
        st.balloons()

    # ── Results ──────────────────────────────────────────────────────────
    if st.session_state.results:
        st.markdown("---")
        st.markdown("### Your Applications")

        # Sort by score descending
        sorted_results = sorted(
            st.session_state.results.items(),
            key=lambda x: x[1]["match"].get("match_score", 0),
            reverse=True,
        )

        for orig_idx, result in sorted_results:
            job   = result["job"]
            match = result["match"]
            score = match.get("match_score", 0)
            ring  = _score_class(score)

            header = f"{job['title']} at {job['company']} — {score}% match"
            with st.expander(header, expanded=(score >= 65)):

                # ── Score + skills row ──
                sc1, sc2, sc3 = st.columns([1, 2, 2])
                with sc1:
                    st.markdown(
                        f'<div class="score-ring {ring}">{score}%</div>'
                        f'<p style="text-align:center;font-size:0.72rem;color:#64748b;margin-top:4px">match score</p>',
                        unsafe_allow_html=True,
                    )
                with sc2:
                    if match.get("matching_skills"):
                        st.markdown("**✅ You have**")
                        chips = "".join(f'<span class="chip chip-good">{s}</span>' for s in match["matching_skills"][:8])
                        st.markdown(chips, unsafe_allow_html=True)
                with sc3:
                    if match.get("missing_skills"):
                        st.markdown("**⚠️ Gaps to address**")
                        chips = "".join(f'<span class="chip chip-missing">{s}</span>' for s in match["missing_skills"][:8])
                        st.markdown(chips, unsafe_allow_html=True)

                if match.get("summary"):
                    st.info(match["summary"])

                # ── Action checklist ──
                actions = result.get("manual_actions", [])
                if actions:
                    priority_order = {"high": 0, "medium": 1, "low": 2}
                    priority_icon  = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                    cat_label      = {"verification": "Verify", "personalization": "Personalise",
                                      "portfolio": "Portfolio", "authenticity": "Authenticity", "formatting": "Format"}
                    with st.expander("📋 Before you submit — action checklist", expanded=True):
                        for a in sorted(actions, key=lambda x: priority_order.get(x.get("priority","low"), 2)):
                            icon = priority_icon.get(a.get("priority","low"), "🟢")
                            cat  = cat_label.get(a.get("category",""), a.get("category","").title())
                            st.markdown(
                                f'<div class="action-row">'
                                f'<span style="font-size:1rem">{icon}</span>'
                                f'<div><strong>[{cat}]</strong> {a.get("action","")}'
                                f'<br><span style="font-size:0.78rem;color:#64748b">{a.get("reason","")}</span></div>'
                                f'</div>',
                                unsafe_allow_html=True,
                            )

                st.markdown("---")

                # ── Downloads + apply ──
                from utils.resume_writer import create_tailored_docx, create_cover_letter_docx
                _cn = st.session_state.get("candidate_name", "Candidate")
                d1, d2, d3 = st.columns(3)

                with d1:
                    st.markdown("**📄 Tailored Resume**")
                    r_text = result.get("edited_resume") or result["tailored_text"]
                    r_file = result.get("resume_path", "")
                    if result.get("edited_resume"):
                        tmp = os.path.join(st.session_state.tmp_dir, f"Edited_R_{orig_idx}.docx")
                        create_tailored_docx(r_text, job, tmp, _cn)
                        r_file = tmp
                    if r_file and os.path.exists(r_file):
                        with open(r_file, "rb") as f:
                            st.download_button(
                                "⬇️ Download Resume",
                                data=f.read(),
                                file_name=os.path.basename(r_file),
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"dl_r_{orig_idx}",
                                use_container_width=True,
                                type="primary",
                            )

                with d2:
                    cover_text = result.get("edited_cover") or result.get("cover_text", "")
                    if cover_text:
                        st.markdown("**📝 Cover Letter**")
                        c_file = result.get("cover_path", "")
                        if result.get("edited_cover"):
                            tmp = os.path.join(st.session_state.tmp_dir, f"Edited_C_{orig_idx}.docx")
                            create_cover_letter_docx(cover_text, job, tmp, _cn)
                            c_file = tmp
                        if c_file and os.path.exists(c_file):
                            with open(c_file, "rb") as f:
                                st.download_button(
                                    "⬇️ Download Cover Letter",
                                    data=f.read(),
                                    file_name=os.path.basename(c_file),
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key=f"dl_c_{orig_idx}",
                                    use_container_width=True,
                                )

                with d3:
                    if job.get("url"):
                        st.markdown("**🚀 Apply**")
                        st.link_button(
                            "Open job posting ↗",
                            job["url"],
                            use_container_width=True,
                        )
                        st.caption("Tip: download both files first, then open the posting")

                # ── Edit tabs ──
                et1, et2 = st.tabs(["✏️ Edit resume", "✏️ Edit cover letter"])
                with et1:
                    cur_r = result.get("edited_resume") or result["tailored_text"]
                    new_r = st.text_area("", value=cur_r, height=380, key=f"er_{orig_idx}", label_visibility="collapsed")
                    s1, s2 = st.columns([3, 1])
                    with s1:
                        if st.button("💾 Save edits", key=f"sr_{orig_idx}", use_container_width=True):
                            st.session_state.results[orig_idx]["edited_resume"] = new_r
                            st.success("Saved — re-download to get the updated file.")
                    with s2:
                        if st.button("↺ Reset", key=f"rr_{orig_idx}", use_container_width=True):
                            st.session_state.results[orig_idx]["edited_resume"] = None
                            st.rerun()

                with et2:
                    if result.get("cover_text"):
                        cur_c = result.get("edited_cover") or result["cover_text"]
                        new_c = st.text_area("", value=cur_c, height=320, key=f"ec_{orig_idx}", label_visibility="collapsed")
                        s3, s4 = st.columns([3, 1])
                        with s3:
                            if st.button("💾 Save edits", key=f"sc_{orig_idx}", use_container_width=True):
                                st.session_state.results[orig_idx]["edited_cover"] = new_c
                                st.success("Saved — re-download to get the updated file.")
                        with s4:
                            if st.button("↺ Reset", key=f"rc_{orig_idx}", use_container_width=True):
                                st.session_state.results[orig_idx]["edited_cover"] = None
                                st.rerun()
                    else:
                        st.caption("No cover letter was generated for this job.")


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — TRACKER
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## 📊 Application Tracker")

    from utils.excel_tracker import get_all_applications, TRACKER_FILE
    import pandas as pd

    applications = get_all_applications()

    if not applications:
        st.markdown(
            '<div class="upload-hint">'
            '<h3 style="margin:0 0 0.5rem">No applications tracked yet</h3>'
            '<p style="margin:0">Process jobs in the <strong>⚡ AI Apply</strong> tab — '
            'they\'ll appear here automatically.</p>'
            '</div>', unsafe_allow_html=True,
        )
        if os.path.exists(TRACKER_FILE):
            with open(TRACKER_FILE, "rb") as f:
                st.download_button("⬇️ Download empty tracker template", data=f,
                    file_name="JobPilot_Tracker.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    else:
        total  = len(applications)
        stats  = [a.get("Status", "") for a in applications]
        n_app  = stats.count("Applied")
        n_int  = stats.count("Interviewing")
        n_off  = stats.count("Offer")
        n_rej  = stats.count("Rejected")

        # Stat row
        cs1, cs2, cs3, cs4, cs5 = st.columns(5)
        for col, label, val, color in [
            (cs1, "Total", total, "#6366f1"),
            (cs2, "Applied", n_app, "#64748b"),
            (cs3, "Interviewing", n_int, "#f59e0b"),
            (cs4, "Offers", n_off, "#10b981"),
            (cs5, "Rejected", n_rej, "#ef4444"),
        ]:
            with col:
                st.markdown(
                    f'<div class="stat-box"><div class="stat-num" style="color:{color}">{val}</div>'
                    f'<div class="stat-label">{label}</div></div>',
                    unsafe_allow_html=True,
                )

        st.markdown("---")

        # Filters
        tf1, tf2, tf3 = st.columns([2, 2, 2])
        with tf1:
            f_status = st.selectbox("Status", ["All", "Applied", "Interviewing", "Offer", "Rejected", "Withdrawn"])
        with tf2:
            f_company = st.text_input("Filter by company", placeholder="Type to filter…")
        with tf3:
            f_sort = st.selectbox("Sort by", ["Date (newest)", "Match score", "Company"])

        filtered = applications
        if f_status != "All":
            filtered = [a for a in filtered if a.get("Status") == f_status]
        if f_company:
            filtered = [a for a in filtered if f_company.lower() in str(a.get("Company","")).lower()]
        if f_sort == "Match score":
            filtered.sort(key=lambda x: int(str(x.get("Match Score","0")).rstrip("%") or 0), reverse=True)
        elif f_sort == "Company":
            filtered.sort(key=lambda x: str(x.get("Company","")))
        else:
            filtered.sort(key=lambda x: str(x.get("Date Applied","")), reverse=True)

        st.caption(f"Showing {len(filtered)} of {total} applications")
        df = pd.DataFrame(filtered)
        if not df.empty:
            st.dataframe(
                df, use_container_width=True, hide_index=True,
                column_config={
                    "Job URL": st.column_config.LinkColumn("Job URL"),
                    "Match Score": st.column_config.TextColumn("Match %"),
                    "Status": st.column_config.SelectboxColumn(
                        "Status", options=["Applied","Interviewing","Offer","Rejected","Withdrawn"],
                    ),
                },
            )

        if os.path.exists(TRACKER_FILE):
            with open(TRACKER_FILE, "rb") as f:
                st.download_button(
                    "⬇️ Download Excel tracker",
                    data=f, file_name="JobPilot_Applications.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                )
