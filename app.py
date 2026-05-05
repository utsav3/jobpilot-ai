"""
JobPilot AI — Smart Job Application System
Run: streamlit run app.py
"""
import streamlit as st
import os
import tempfile
import shutil
import webbrowser
from pathlib import Path
from datetime import datetime

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="JobPilot AI",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

.main-title {
    font-size: 2.2rem; font-weight: 700;
    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0;
}
.subtitle { color: #64748b; font-size: 1rem; margin-top: 0; }

.job-card {
    background: #ffffff; border-radius: 12px; padding: 1.1rem 1.3rem;
    border: 1px solid #e2e8f0; margin-bottom: 0.8rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06);
    transition: box-shadow 0.2s;
}
.job-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }

.score-pill {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 0.75rem; font-weight: 700; letter-spacing: 0.3px;
}
.score-high   { background: #dcfce7; color: #166534; }
.score-medium { background: #fef9c3; color: #713f12; }
.score-low    { background: #fee2e2; color: #991b1b; }

.stat-box {
    background: white; border-radius: 10px; padding: 1rem;
    border: 1px solid #e2e8f0; text-align: center;
}
.stat-number { font-size: 1.8rem; font-weight: 700; color: #0f3460; }
.stat-label  { font-size: 0.78rem; color: #64748b; margin-top: 2px; }

.step-badge {
    display: inline-flex; align-items: center; justify-content: center;
    width: 26px; height: 26px; border-radius: 50%;
    background: #0f3460; color: white; font-size: 0.75rem; font-weight: 700;
    margin-right: 8px;
}
.section-header {
    font-weight: 600; font-size: 1rem; color: #1e293b;
    padding: 0.4rem 0; border-bottom: 2px solid #e2e8f0;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)


# ── Session State ────────────────────────────────────────────────────────────
def _init():
    defaults = {
        "resumes": [],          # [{name, text, path, format}]
        "active_resume_idx": 0,
        "jobs": [],             # [job_dict, ...]
        "selected_jobs": set(),
        "results": {},          # job_idx -> {match, tailored, cover_letter, manual_actions, ...}
        "tmp_dir": tempfile.mkdtemp(prefix="jobpilot_"),
        "job_suggestions": None,    # dict from suggest_job_searches()
        "search_prefill": {},       # {"keywords": str, "location": str}
        "candidate_name": "",       # cached for use in results display
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

_init()


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="main-title">🚀 JobPilot AI</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Smart job application system</p>', unsafe_allow_html=True)
    st.divider()

    st.markdown("### 🤖 AI / LLM")
    from utils.ai_tailor import get_provider, get_provider_label, is_deployed
    provider_label = get_provider_label()
    env_label = "☁️ Deployed" if is_deployed() else "💻 Local"
    if get_provider() == "none":
        st.error(f"{env_label} · ⚠️ No LLM key set")
    elif get_provider() == "ollama":
        st.info(f"{env_label} · **{provider_label}**")
    else:
        st.success(f"{env_label} · **{provider_label}**")

    anthropic_key = st.text_input(
        "Anthropic API Key (Claude)",
        value=os.getenv("ANTHROPIC_API_KEY", ""),
        type="password",
        help="console.anthropic.com — Haiku is fast and cheap",
    )
    google_key = st.text_input(
        "Google API Key (Gemini — free)",
        value=os.getenv("GOOGLE_API_KEY", ""),
        type="password",
        help="aistudio.google.com → Get API key — 1M tokens/day free",
    )
    openai_key = st.text_input(
        "OpenAI API Key",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
    )

    st.divider()

    st.markdown("### 🔑 Job Search API Keys")
    st.caption("The Muse and RemoteOK work without any keys.")

    serpapi_key = st.text_input(
        "SerpAPI Key ⭐ (Google Jobs)",
        value=os.getenv("SERPAPI_KEY", ""),
        type="password",
        help="Best source — aggregates LinkedIn, Indeed, Glassdoor. 100 free searches/month at serpapi.com",
    )
    rapidapi_key = st.text_input(
        "RapidAPI Key (JSearch / LinkedIn / Indeed)",
        value=os.getenv("RAPIDAPI_KEY", ""),
        type="password",
        help="Free tier at rapidapi.com — search 'JSearch' to subscribe",
    )
    adzuna_id = st.text_input(
        "Adzuna App ID",
        value=os.getenv("ADZUNA_APP_ID", ""),
        type="password",
        help="Free at developer.adzuna.com",
    )
    adzuna_key = st.text_input(
        "Adzuna API Key",
        value=os.getenv("ADZUNA_API_KEY", ""),
        type="password",
    )

    if st.button("💾 Save Keys", use_container_width=True):
        if anthropic_key:
            os.environ["ANTHROPIC_API_KEY"] = anthropic_key
        if google_key:
            os.environ["GOOGLE_API_KEY"] = google_key
        if openai_key:
            os.environ["OPENAI_API_KEY"] = openai_key
        os.environ["SERPAPI_KEY"] = serpapi_key
        os.environ["RAPIDAPI_KEY"] = rapidapi_key
        os.environ["ADZUNA_APP_ID"] = adzuna_id
        os.environ["ADZUNA_API_KEY"] = adzuna_key
        st.success("Keys saved!")
        st.rerun()

    # Show active sources
    from utils.job_search import get_active_sources
    active_srcs = get_active_sources()
    st.caption("**Job sources:** " + ", ".join(active_srcs))

    st.divider()

    # Status indicators
    st.markdown("### 📊 Status")
    col1, col2 = st.columns(2)
    with col1:
        r_count = len(st.session_state.resumes)
        st.metric("Resumes", r_count)
    with col2:
        j_count = len(st.session_state.jobs)
        st.metric("Jobs Found", j_count)

    sel_count = len(st.session_state.selected_jobs)
    proc_count = len(st.session_state.results)
    col3, col4 = st.columns(2)
    with col3:
        st.metric("Selected", sel_count)
    with col4:
        st.metric("Processed", proc_count)

    st.divider()
    st.caption("v1.0 · Built with Claude + Streamlit")


# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📄 Resumes",
    "🔍 Job Search",
    "🤖 AI Apply",
    "📊 Tracker",
])


# ════════════════════════════════════════════════════════════════════════════
# TAB 1 — RESUMES
# ════════════════════════════════════════════════════════════════════════════
with tab1:
    st.markdown("## 📄 Resume Manager")
    st.caption("Upload one or more resume versions. The AI will use the selected one as the base.")

    uploaded = st.file_uploader(
        "Upload resume(s)",
        type=["pdf", "docx"],
        accept_multiple_files=True,
        label_visibility="collapsed",
    )

    if uploaded:
        from utils.resume_parser import parse_resume, extract_name_from_resume

        new_names = {r["name"] for r in st.session_state.resumes}
        added = 0
        for f in uploaded:
            if f.name in new_names:
                continue
            save_path = os.path.join(st.session_state.tmp_dir, f.name)
            with open(save_path, "wb") as fp:
                fp.write(f.read())
            try:
                parsed = parse_resume(save_path)
                parsed["display_name"] = f.name
                st.session_state.resumes.append(parsed)
                added += 1
                new_names.add(f.name)
            except Exception as e:
                st.error(f"Failed to parse {f.name}: {e}")

        if added:
            st.success(f"✅ Added {added} resume(s).")

    if not st.session_state.resumes:
        st.info("⬆️ Upload at least one resume (PDF or DOCX) to get started.")
    else:
        st.markdown("### Your Resumes")

        for i, resume in enumerate(st.session_state.resumes):
            is_active = st.session_state.active_resume_idx == i
            border_style = "border: 2px solid #0f3460;" if is_active else "border: 1px solid #e2e8f0;"
            with st.container():
                st.markdown(
                    f'<div class="job-card" style="{border_style}">',
                    unsafe_allow_html=True,
                )
                col_a, col_b, col_c = st.columns([5, 2, 2])
                with col_a:
                    badge = "🟢 Active" if is_active else "⚪ Inactive"
                    st.markdown(f"**{resume['display_name']}** &nbsp; {badge}", unsafe_allow_html=True)
                    preview = resume["raw_text"][:180].replace("\n", " ")
                    st.caption(f"{preview}…")
                with col_b:
                    st.caption(f"Format: `{resume['format'].upper()}`")
                    word_count = len(resume["raw_text"].split())
                    st.caption(f"~{word_count} words")
                with col_c:
                    if not is_active:
                        if st.button("Set Active", key=f"active_{i}"):
                            st.session_state.active_resume_idx = i
                            st.rerun()
                    if st.button("Remove", key=f"remove_{i}"):
                        st.session_state.resumes.pop(i)
                        if st.session_state.active_resume_idx >= len(st.session_state.resumes):
                            st.session_state.active_resume_idx = 0
                        st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.resumes:
            with st.expander("👁️ Preview Active Resume Text"):
                active = st.session_state.resumes[st.session_state.active_resume_idx]
                st.text_area("", active["raw_text"], height=400, label_visibility="collapsed")


# ════════════════════════════════════════════════════════════════════════════
# TAB 2 — JOB SEARCH
# ════════════════════════════════════════════════════════════════════════════
with tab2:
    st.markdown("## 🔍 Job Search")
    from utils.job_search import get_active_sources
    active_srcs = get_active_sources()
    st.caption(f"Searching across: **{', '.join(active_srcs)}**. Results are deduplicated automatically.")

    # ── AI Job Recommendations ──────────────────────────────────────────────
    if st.session_state.resumes:
        st.markdown("### 🎯 AI Job Recommendations")
        st.caption("Let the AI analyze your resume and suggest what to search for.")

        col_suggest, col_clear = st.columns([3, 1])
        with col_suggest:
            suggest_btn = st.button(
                "🎯 Recommend Jobs for Me",
                type="secondary",
                use_container_width=True,
            )
        with col_clear:
            if st.session_state.job_suggestions:
                if st.button("✕ Clear Suggestions", use_container_width=True):
                    st.session_state.job_suggestions = None
                    st.session_state.search_prefill = {}
                    st.rerun()

        if suggest_btn:
            from utils.ai_tailor import suggest_job_searches
            active_r = st.session_state.resumes[st.session_state.active_resume_idx]
            with st.spinner("Analyzing your resume…"):
                st.session_state.job_suggestions = suggest_job_searches(active_r["raw_text"])
            st.rerun()

        if st.session_state.job_suggestions:
            sugg = st.session_state.job_suggestions
            exp_level = sugg.get("experience_level", "")
            if exp_level and exp_level != "unknown":
                st.caption(f"Detected experience level: **{exp_level}**")

            all_titles = sugg.get("primary_titles", []) + sugg.get("alternative_titles", [])
            if all_titles:
                st.markdown("**Relevant job titles:** " + "  ·  ".join(f"`{t}`" for t in all_titles))

            st.markdown("**Suggested searches:**")
            for i, s in enumerate(sugg.get("suggested_searches", [])):
                col_info, col_btn = st.columns([5, 2])
                with col_info:
                    loc_type = s.get("location_type", "any")
                    loc_icon = {"remote": "🌐", "onsite": "🏢", "hybrid": "🔄"}.get(loc_type, "📍")
                    st.markdown(f"{loc_icon} **{s['keywords']}**")
                    st.caption(s.get("rationale", ""))
                with col_btn:
                    if st.button("Use This Search", key=f"use_sugg_{i}", use_container_width=True):
                        st.session_state.search_prefill = {
                            "keywords": s["keywords"],
                            "location": "Remote" if s.get("location_type") == "remote" else "",
                        }
                        st.rerun()

        st.divider()

    with st.form("search_form"):
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            keywords = st.text_input(
                "Job Title / Keywords *",
                value=st.session_state.search_prefill.get("keywords", ""),
                placeholder="e.g. Software Engineer, Data Scientist",
            )
        with col2:
            country = st.selectbox(
                "Country",
                options=["United States", "United Kingdom", "Canada", "Australia", "Germany"],
                index=0,
            )
        with col3:
            num_results = st.number_input("Max Results", 5, 50, 20)

        location = st.text_input(
            "City / State (optional)",
            value=st.session_state.search_prefill.get("location", ""),
            placeholder="e.g. New York, NY · San Francisco · Remote  (leave blank to search all of the country)",
        )

        col4, col5 = st.columns([2, 2])
        with col4:
            remote_only = st.checkbox("Remote only")
        with col5:
            min_salary = st.number_input("Min. Salary ($)", 0, 500000, 0, step=10000)

        search_btn = st.form_submit_button("🔍 Search Jobs", use_container_width=True, type="primary")

    if search_btn:
        st.session_state.search_prefill = {}
        if not keywords:
            st.warning("Please enter job title or keywords.")
        else:
            from utils.job_search import search_jobs
            loc_display = f"{location}, {country}" if location else country
            with st.spinner(f"Searching {loc_display}..."):
                jobs = search_jobs(keywords, location, country=country, num=num_results)

            # Apply filters
            if remote_only:
                jobs = [j for j in jobs if j.get("remote") or "remote" in (j.get("title", "") + j.get("location", "")).lower()]
            if min_salary > 0:
                jobs = [j for j in jobs if (j.get("salary_min") or 0) >= min_salary or (j.get("salary_max") or 0) >= min_salary]

            st.session_state.jobs = jobs
            st.session_state.selected_jobs = set()

            if jobs:
                st.success(f"Found **{len(jobs)}** jobs in **{loc_display}**.")
            else:
                st.warning("No results found. Try broader keywords, a different city, or leave the city field blank to search all of the country.")

    # ── Manual Job Entry ────────────────────────────────────────────────────
    st.divider()
    st.markdown("### 📋 Add a Job Manually")
    st.caption("Paste any job from LinkedIn, Indeed, or anywhere — no API keys needed.")

    with st.expander("➕ Add job manually", expanded=not bool(st.session_state.jobs)):
        with st.form("manual_job_form"):
            mj_col1, mj_col2 = st.columns(2)
            with mj_col1:
                mj_title = st.text_input("Job Title *", placeholder="e.g. Senior Software Engineer")
                mj_company = st.text_input("Company *", placeholder="e.g. Acme Corp")
            with mj_col2:
                mj_location = st.text_input("Location", placeholder="e.g. New York, NY or Remote")
                mj_url = st.text_input("Job URL (optional)", placeholder="https://...")
            mj_desc = st.text_area(
                "Job Description *",
                placeholder="Paste the full job description here…",
                height=200,
            )
            add_job_btn = st.form_submit_button("➕ Add to Job List", use_container_width=True, type="primary")

        if add_job_btn:
            if not mj_title or not mj_company or not mj_desc:
                st.error("Job Title, Company, and Job Description are required.")
            else:
                manual_job = {
                    "title": mj_title.strip(),
                    "company": mj_company.strip(),
                    "location": mj_location.strip() or "Not specified",
                    "description": mj_desc.strip(),
                    "url": mj_url.strip(),
                    "salary_min": None,
                    "salary_max": None,
                    "salary_display": "Not specified",
                    "posted_date": "",
                    "source": "Manual",
                    "employment_type": "",
                    "remote": "remote" in mj_location.lower(),
                }
                # Avoid duplicate by (title, company)
                existing = {
                    (j["title"].lower().strip(), j["company"].lower().strip())
                    for j in st.session_state.jobs
                }
                key = (manual_job["title"].lower(), manual_job["company"].lower())
                if key in existing:
                    st.warning("This job is already in the list.")
                else:
                    st.session_state.jobs.append(manual_job)
                    st.success(f"✅ Added **{mj_title}** at **{mj_company}** to the job list.")
                    st.rerun()

    if st.session_state.jobs:
        st.divider()

        col_sel, col_clr = st.columns([3, 1])
        with col_sel:
            st.markdown(f"### Results ({len(st.session_state.jobs)} jobs)")
        with col_clr:
            if st.button("☑️ Select All"):
                st.session_state.selected_jobs = set(range(len(st.session_state.jobs)))
                st.rerun()
            if st.button("☐ Deselect All"):
                st.session_state.selected_jobs = set()
                st.rerun()

        for idx, job in enumerate(st.session_state.jobs):
            is_selected = idx in st.session_state.selected_jobs
            border = "border: 2px solid #0f3460;" if is_selected else ""

            with st.container():
                st.markdown(f'<div class="job-card" style="{border}">', unsafe_allow_html=True)

                row1, row2 = st.columns([6, 1])
                with row1:
                    st.markdown(f"**{job['title']}** at **{job['company']}**")
                    meta_parts = [f"📍 {job['location']}"]
                    if job.get("salary_display") and job["salary_display"] != "Not specified":
                        meta_parts.append(f"💰 {job['salary_display']}")
                    if job.get("employment_type"):
                        meta_parts.append(f"🕐 {job['employment_type']}")
                    if job.get("remote"):
                        meta_parts.append("🌐 Remote")
                    meta_parts.append(f"🔗 {job['source']}")
                    if job.get("posted_date"):
                        meta_parts.append(f"📅 {job['posted_date']}")
                    st.caption("  ·  ".join(meta_parts))
                with row2:
                    if is_selected:
                        if st.button("✅ Selected", key=f"sel_{idx}"):
                            st.session_state.selected_jobs.discard(idx)
                            st.rerun()
                    else:
                        if st.button("+ Select", key=f"sel_{idx}"):
                            st.session_state.selected_jobs.add(idx)
                            st.rerun()

                with st.expander("📄 Job Description"):
                    desc = job.get("description", "No description available.")
                    st.write(desc[:1500] + ("…" if len(desc) > 1500 else ""))
                    if job.get("url"):
                        st.link_button("🔗 View Full Posting", job["url"])

                st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.selected_jobs:
            st.success(f"**{len(st.session_state.selected_jobs)}** job(s) selected. Go to the **🤖 AI Apply** tab to process them.")


# ════════════════════════════════════════════════════════════════════════════
# TAB 3 — AI APPLY
# ════════════════════════════════════════════════════════════════════════════
with tab3:
    st.markdown("## 🤖 AI-Powered Application")

    # Guard checks
    if not st.session_state.resumes:
        st.warning("⬅️ Upload at least one resume in the **📄 Resumes** tab first.")
        st.stop()
    if not st.session_state.selected_jobs:
        st.warning("⬅️ Select jobs in the **🔍 Job Search** tab first.")
        st.stop()
    from utils.ai_tailor import get_provider, get_provider_label, is_deployed
    provider = get_provider()
    if provider == "none":
        st.error(
            "No LLM API key is set. Add **ANTHROPIC_API_KEY**, **GOOGLE_API_KEY**, "
            "or **OPENAI_API_KEY** in your Render environment variables, then redeploy."
        )
        st.stop()
    if provider == "ollama":
        import urllib.request
        try:
            urllib.request.urlopen("http://localhost:11434/api/tags", timeout=2)
        except Exception:
            st.warning(
                "Ollama is not running. Start it with `ollama serve` — "
                "or add a cloud key (Claude / Gemini / OpenAI) in the sidebar."
            )
            st.stop()

    active_resume = st.session_state.resumes[st.session_state.active_resume_idx]
    selected_indices = sorted(st.session_state.selected_jobs)
    selected_jobs = [st.session_state.jobs[i] for i in selected_indices]

    st.info(f"Using resume: **{active_resume['display_name']}** · Processing **{len(selected_jobs)}** job(s)")

    from utils.resume_parser import extract_name_from_resume
    candidate_name = extract_name_from_resume(active_resume["raw_text"])
    st.session_state.candidate_name = candidate_name

    # Options
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        gen_cover = st.checkbox("Generate Cover Letters", value=True)
    with col_opt2:
        auto_track = st.checkbox("Auto-add to Tracker", value=True)

    # Process all button
    if st.button("⚡ Process All Selected Jobs", type="primary", use_container_width=True):
        from utils.ai_tailor import analyze_match, tailor_resume, generate_cover_letter, generate_manual_actions
        from utils.excel_tracker import add_application
        from utils.resume_writer import create_tailored_docx, create_cover_letter_docx

        progress_bar = st.progress(0, text="Initializing…")
        status_text = st.empty()

        for i, (orig_idx, job) in enumerate(zip(selected_indices, selected_jobs)):
            pct = int((i / len(selected_jobs)) * 100)
            progress_bar.progress(pct, text=f"Processing: {job['title']} at {job['company']}")

            try:
                # 1. Match analysis
                status_text.caption(f"🔍 Analyzing match for {job['title']}…")
                match = analyze_match(active_resume["raw_text"], job)

                # 2. Tailor resume
                status_text.caption(f"✏️ Tailoring resume for {job['title']}…")
                tailored_text = tailor_resume(active_resume["raw_text"], job)

                # 3. Cover letter
                cover_text = ""
                if gen_cover:
                    status_text.caption(f"📝 Writing cover letter for {job['title']}…")
                    cover_text = generate_cover_letter(active_resume["raw_text"], job, candidate_name)

                # 4. Generate manual action checklist (isolated — never blocks pipeline)
                manual_actions = []
                try:
                    status_text.caption(f"📋 Generating action checklist for {job['title']}…")
                    manual_actions = generate_manual_actions(
                        active_resume["raw_text"], job, tailored_text, cover_text
                    )
                except Exception:
                    pass

                # 5. Generate DOCX files
                safe_company = "".join(c for c in job["company"] if c.isalnum() or c in " -_")[:30]
                safe_title = "".join(c for c in job["title"] if c.isalnum() or c in " -_")[:30]
                base_name = f"{safe_company}_{safe_title}".replace(" ", "_")

                resume_path = os.path.join(st.session_state.tmp_dir, f"Resume_{base_name}.docx")
                create_tailored_docx(tailored_text, job, resume_path, candidate_name)

                cover_path = ""
                if gen_cover and cover_text:
                    cover_path = os.path.join(st.session_state.tmp_dir, f"CoverLetter_{base_name}.docx")
                    create_cover_letter_docx(cover_text, job, cover_path, candidate_name)

                # 6. Track
                if auto_track:
                    add_application(
                        job,
                        match.get("match_score", 0),
                        active_resume["display_name"],
                        has_cover_letter=bool(cover_text),
                    )

                # Save result
                st.session_state.results[orig_idx] = {
                    "match": match,
                    "tailored_text": tailored_text,
                    "cover_text": cover_text,
                    "resume_path": resume_path,
                    "cover_path": cover_path,
                    "job": job,
                    "manual_actions": manual_actions,
                    "edited_resume": None,
                    "edited_cover": None,
                }

            except Exception as e:
                st.error(f"Error processing {job['title']}: {e}")

        progress_bar.progress(100, text="✅ All done!")
        status_text.empty()
        st.success(f"🎉 Processed {len(selected_jobs)} job(s)! Scroll down to review and apply.")
        st.balloons()

    # ── Results ──
    if st.session_state.results:
        st.divider()
        st.markdown("### 📋 Results & Applications")

        for orig_idx, result in st.session_state.results.items():
            job = result["job"]
            match = result["match"]
            score = match.get("match_score", 0)

            score_cls = "score-high" if score >= 75 else ("score-medium" if score >= 50 else "score-low")

            with st.expander(
                f"**{job['title']}** at {job['company']} — "
                f"Match: {score}%",
                expanded=score >= 60,
            ):
                # Match analysis
                col_m1, col_m2, col_m3 = st.columns([1, 2, 2])
                with col_m1:
                    st.markdown(f'<div class="stat-box"><div class="stat-number">{score}%</div><div class="stat-label">Match Score</div></div>', unsafe_allow_html=True)
                with col_m2:
                    if match.get("matching_skills"):
                        st.markdown("**✅ Matching Skills**")
                        st.write(", ".join(match["matching_skills"][:8]))
                with col_m3:
                    if match.get("missing_skills"):
                        st.markdown("**⚠️ Skills to Highlight**")
                        st.write(", ".join(match["missing_skills"][:8]))

                if match.get("summary"):
                    st.info(f"💡 {match['summary']}")

                # Manual action checklist
                manual_actions = result.get("manual_actions", [])
                if manual_actions:
                    priority_order = {"high": 0, "medium": 1, "low": 2}
                    sorted_actions = sorted(
                        manual_actions,
                        key=lambda x: priority_order.get(x.get("priority", "low"), 2),
                    )
                    priority_icons = {"high": "🔴", "medium": "🟡", "low": "🟢"}
                    category_labels = {
                        "verification": "Verify",
                        "personalization": "Personalize",
                        "portfolio": "Portfolio",
                        "authenticity": "Authenticity",
                        "formatting": "Formatting",
                    }
                    with st.expander("⚠️ Before You Apply — Action Items", expanded=True):
                        for action_item in sorted_actions:
                            priority = action_item.get("priority", "low")
                            category = action_item.get("category", "")
                            icon = priority_icons.get(priority, "🟢")
                            cat_label = category_labels.get(category, category.title())
                            col_icon, col_content = st.columns([1, 12])
                            with col_icon:
                                st.markdown(f"### {icon}")
                            with col_content:
                                st.markdown(f"**[{cat_label}]** {action_item.get('action', '')}")
                                if action_item.get("reason"):
                                    st.caption(action_item["reason"])

                st.divider()

                # Download buttons — use edited version if available
                from utils.resume_writer import create_tailored_docx, create_cover_letter_docx
                _cname = st.session_state.get("candidate_name", "Candidate")

                doc_col1, doc_col2, doc_col3 = st.columns([2, 2, 2])

                with doc_col1:
                    st.markdown("**📄 Tailored Resume**")
                    edited_r_text = result.get("edited_resume")
                    if edited_r_text:
                        tmp_edited_r = os.path.join(
                            st.session_state.tmp_dir, f"Edited_Resume_{orig_idx}.docx"
                        )
                        create_tailored_docx(edited_r_text, job, tmp_edited_r, _cname)
                        with open(tmp_edited_r, "rb") as f:
                            st.download_button(
                                "⬇️ Download Resume (.docx) ✏️",
                                data=f.read(),
                                file_name=os.path.basename(result["resume_path"]),
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"dl_resume_{orig_idx}",
                                use_container_width=True,
                            )
                    elif os.path.exists(result.get("resume_path", "")):
                        with open(result["resume_path"], "rb") as f:
                            st.download_button(
                                "⬇️ Download Resume (.docx)",
                                data=f.read(),
                                file_name=os.path.basename(result["resume_path"]),
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                key=f"dl_resume_{orig_idx}",
                                use_container_width=True,
                            )

                with doc_col2:
                    edited_c_text = result.get("edited_cover")
                    has_cover = result.get("cover_text") or edited_c_text
                    if has_cover:
                        st.markdown("**📝 Cover Letter**")
                        if edited_c_text:
                            tmp_edited_c = os.path.join(
                                st.session_state.tmp_dir, f"Edited_Cover_{orig_idx}.docx"
                            )
                            create_cover_letter_docx(edited_c_text, job, tmp_edited_c, _cname)
                            with open(tmp_edited_c, "rb") as f:
                                st.download_button(
                                    "⬇️ Download Cover Letter (.docx) ✏️",
                                    data=f.read(),
                                    file_name=os.path.basename(result["cover_path"]),
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key=f"dl_cover_{orig_idx}",
                                    use_container_width=True,
                                )
                        elif result.get("cover_path") and os.path.exists(result["cover_path"]):
                            with open(result["cover_path"], "rb") as f:
                                st.download_button(
                                    "⬇️ Download Cover Letter (.docx)",
                                    data=f.read(),
                                    file_name=os.path.basename(result["cover_path"]),
                                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                                    key=f"dl_cover_{orig_idx}",
                                    use_container_width=True,
                                )

                with doc_col3:
                    if job.get("url"):
                        st.markdown("**🚀 Apply Now**")
                        st.link_button(
                            "🔗 Open Job Posting",
                            job["url"],
                            use_container_width=True,
                        )

                # Editable tabs
                tab_r, tab_c = st.tabs(["✏️ Edit Resume", "✏️ Edit Cover Letter"])

                with tab_r:
                    current_r = result.get("edited_resume") or result["tailored_text"]
                    edited_r = st.text_area(
                        "Tailored Resume",
                        value=current_r,
                        height=400,
                        key=f"edit_r_{orig_idx}",
                        label_visibility="collapsed",
                        help="Edit directly. Click 'Save Edits' to use your changes in the download.",
                    )
                    col_save_r, col_reset_r = st.columns([2, 1])
                    with col_save_r:
                        if st.button("💾 Save Resume Edits", key=f"save_r_{orig_idx}", use_container_width=True):
                            st.session_state.results[orig_idx]["edited_resume"] = edited_r
                            st.success("Resume edits saved — re-download to get the updated file.")
                    with col_reset_r:
                        if st.button("↺ Reset to AI Version", key=f"reset_r_{orig_idx}", use_container_width=True):
                            st.session_state.results[orig_idx]["edited_resume"] = None
                            st.rerun()

                with tab_c:
                    if result.get("cover_text"):
                        current_c = result.get("edited_cover") or result["cover_text"]
                        edited_c = st.text_area(
                            "Cover Letter",
                            value=current_c,
                            height=350,
                            key=f"edit_c_{orig_idx}",
                            label_visibility="collapsed",
                            help="Edit directly. Click 'Save Edits' to use your changes in the download.",
                        )
                        col_save_c, col_reset_c = st.columns([2, 1])
                        with col_save_c:
                            if st.button("💾 Save Cover Letter Edits", key=f"save_c_{orig_idx}", use_container_width=True):
                                st.session_state.results[orig_idx]["edited_cover"] = edited_c
                                st.success("Cover letter edits saved — re-download to get the updated file.")
                        with col_reset_c:
                            if st.button("↺ Reset to AI Version", key=f"reset_c_{orig_idx}", use_container_width=True):
                                st.session_state.results[orig_idx]["edited_cover"] = None
                                st.rerun()
                    else:
                        st.caption("No cover letter generated.")


# ════════════════════════════════════════════════════════════════════════════
# TAB 4 — TRACKER
# ════════════════════════════════════════════════════════════════════════════
with tab4:
    st.markdown("## 📊 Application Tracker")

    from utils.excel_tracker import get_all_applications, TRACKER_FILE, HEADERS

    applications = get_all_applications()

    if applications:
        # Stats row
        total = len(applications)
        statuses = [a.get("Status", "") for a in applications]
        applied_n = statuses.count("Applied")
        interviewing_n = statuses.count("Interviewing")
        offers_n = statuses.count("Offer")

        c1, c2, c3, c4 = st.columns(4)
        for col, label, val, color in [
            (c1, "Total Applied", total, "#0f3460"),
            (c2, "In Progress", interviewing_n, "#D97706"),
            (c3, "Offers", offers_n, "#059669"),
            (c4, "Pending Response", applied_n, "#6B7280"),
        ]:
            with col:
                st.markdown(
                    f'<div class="stat-box"><div class="stat-number" style="color:{color}">{val}</div>'
                    f'<div class="stat-label">{label}</div></div>',
                    unsafe_allow_html=True,
                )

        st.divider()

        # Filter controls
        fc1, fc2, fc3 = st.columns([2, 2, 2])
        with fc1:
            filter_status = st.selectbox("Filter by Status", ["All", "Applied", "Interviewing", "Offer", "Rejected", "Withdrawn"])
        with fc2:
            filter_company = st.text_input("Filter by Company", "")
        with fc3:
            sort_by = st.selectbox("Sort by", ["Date Applied (newest)", "Match Score (highest)", "Company"])

        # Apply filters
        filtered = applications
        if filter_status != "All":
            filtered = [a for a in filtered if a.get("Status") == filter_status]
        if filter_company:
            filtered = [a for a in filtered if filter_company.lower() in str(a.get("Company", "")).lower()]

        # Sort
        if sort_by == "Match Score (highest)":
            filtered.sort(key=lambda x: int(str(x.get("Match Score", "0")).rstrip("%") or 0), reverse=True)
        elif sort_by == "Company":
            filtered.sort(key=lambda x: str(x.get("Company", "")))
        else:
            filtered.sort(key=lambda x: str(x.get("Date Applied", "")), reverse=True)

        st.markdown(f"**{len(filtered)}** application(s) shown")

        # Table
        import pandas as pd
        df = pd.DataFrame(filtered)
        if not df.empty:
            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Job URL": st.column_config.LinkColumn("Job URL"),
                    "Match Score": st.column_config.TextColumn("Match %"),
                    "Status": st.column_config.SelectboxColumn(
                        "Status",
                        options=["Applied", "Interviewing", "Offer", "Rejected", "Withdrawn"],
                    ),
                },
            )

        # Download tracker
        if os.path.exists(TRACKER_FILE):
            with open(TRACKER_FILE, "rb") as f:
                st.download_button(
                    "⬇️ Download Full Excel Tracker",
                    data=f,
                    file_name=TRACKER_FILE,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    type="primary",
                )

    else:
        st.info("No applications tracked yet. Process jobs in the **🤖 AI Apply** tab to start tracking.")
        if os.path.exists(TRACKER_FILE):
            with open(TRACKER_FILE, "rb") as f:
                st.download_button(
                    "⬇️ Download Empty Tracker Template",
                    data=f,
                    file_name=TRACKER_FILE,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
