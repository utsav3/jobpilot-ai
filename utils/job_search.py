import re
import os
import requests
from typing import List, Dict
from datetime import datetime

COUNTRY_CODES = {
    "United States": "us",
    "United Kingdom": "gb",
    "Canada": "ca",
    "Australia": "au",
    "Germany": "de",
}


def search_adzuna(keywords: str, location: str, country_code: str = "us", num: int = 20) -> List[Dict]:
    app_id = os.getenv("ADZUNA_APP_ID", "")
    api_key = os.getenv("ADZUNA_API_KEY", "")
    if not app_id or not api_key:
        return []

    url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
    params = {
        "app_id": app_id,
        "app_key": api_key,
        "what": keywords,
        "results_per_page": min(num, 50),
        "content-type": "application/json",
    }
    if location:
        params["where"] = location

    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        jobs = []
        for j in r.json().get("results", []):
            salary_min = j.get("salary_min")
            salary_max = j.get("salary_max")
            jobs.append({
                "title": j.get("title", ""),
                "company": j.get("company", {}).get("display_name", "N/A"),
                "location": j.get("location", {}).get("display_name", location or "United States"),
                "description": j.get("description", ""),
                "url": j.get("redirect_url", ""),
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_display": _fmt_salary(salary_min, salary_max),
                "posted_date": j.get("created", "")[:10] if j.get("created") else "",
                "source": "Adzuna",
            })
        return jobs
    except Exception:
        return []


def _detect_source_from_url(url: str) -> str:
    """Detect the original job platform from the apply link URL."""
    if not url:
        return ""
    url_lower = url.lower()
    if "linkedin.com" in url_lower:
        return "LinkedIn"
    if "indeed.com" in url_lower:
        return "Indeed"
    if "glassdoor.com" in url_lower:
        return "Glassdoor"
    if "ziprecruiter.com" in url_lower:
        return "ZipRecruiter"
    if "monster.com" in url_lower:
        return "Monster"
    if "dice.com" in url_lower:
        return "Dice"
    if "greenhouse.io" in url_lower:
        return "Greenhouse"
    if "lever.co" in url_lower:
        return "Lever"
    if "workday.com" in url_lower:
        return "Workday"
    return ""


def search_jsearch(keywords: str, location: str, country: str = "United States", num: int = 20) -> List[Dict]:
    """Search via JSearch (RapidAPI) — aggregates LinkedIn, Indeed, Glassdoor, and more."""
    api_key = os.getenv("RAPIDAPI_KEY", "")
    if not api_key:
        return []

    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }

    # Build query — always anchor to country, optionally a city
    if location:
        query = f"{keywords} in {location}, {country}"
    else:
        query = f"{keywords} in {country}"

    jobs = []
    pages_needed = max(1, min((num + 9) // 10, 3))

    for page in range(1, pages_needed + 1):
        if len(jobs) >= num:
            break
        params = {"query": query, "num_pages": "1", "page": str(page)}
        try:
            r = requests.get(url, headers=headers, params=params, timeout=15)
            r.raise_for_status()
            for j in r.json().get("data", []):
                if len(jobs) >= num:
                    break
                salary_min = j.get("job_min_salary")
                salary_max = j.get("job_max_salary")
                city = j.get("job_city", "")
                country_name = j.get("job_country", "")
                loc = f"{city}, {country_name}".strip(", ")
                posted = j.get("job_posted_at_datetime_utc", "")[:10] if j.get("job_posted_at_datetime_utc") else ""
                apply_link = j.get("job_apply_link", "")
                platform = _detect_source_from_url(apply_link) or j.get("job_publisher", "JSearch")
                jobs.append({
                    "title": j.get("job_title", ""),
                    "company": j.get("employer_name", "N/A"),
                    "location": loc or location or country,
                    "description": j.get("job_description", ""),
                    "url": apply_link,
                    "salary_min": salary_min,
                    "salary_max": salary_max,
                    "salary_display": _fmt_salary(salary_min, salary_max),
                    "posted_date": posted,
                    "source": f"JSearch ({platform})" if platform and platform != "JSearch" else "JSearch",
                    "employment_type": j.get("job_employment_type", ""),
                    "remote": j.get("job_is_remote", False),
                })
        except Exception:
            break

    return jobs


def search_remoteok(keywords: str, num: int = 20) -> List[Dict]:
    """Search RemoteOK — free, no API key. Remote/US-friendly jobs."""
    try:
        headers = {"User-Agent": "JobPilot/1.0"}
        r = requests.get("https://remoteok.com/api", headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()
        jobs = []
        for j in data:
            if not isinstance(j, dict) or not j.get("position"):
                continue
            title = j.get("position", "")
            kw_lower = keywords.lower()
            searchable = (title + " " + " ".join(j.get("tags", []))).lower()
            if not any(k.strip() in searchable for k in kw_lower.split()):
                continue
            salary_min = None
            salary_max = None
            salary_str = j.get("salary", "")
            if salary_str:
                nums = re.findall(r"\d+", salary_str.replace(",", "").replace("k", "000"))
                if len(nums) >= 2:
                    salary_min, salary_max = int(nums[0]), int(nums[1])
                elif len(nums) == 1:
                    salary_min = int(nums[0])
            jobs.append({
                "title": title,
                "company": j.get("company", "N/A"),
                "location": "Remote",
                "description": j.get("description", "") or "",
                "url": j.get("url", ""),
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_display": _fmt_salary(salary_min, salary_max),
                "posted_date": j.get("date", "")[:10] if j.get("date") else "",
                "source": "RemoteOK",
                "employment_type": "",
                "remote": True,
            })
            if len(jobs) >= num:
                break
        return jobs
    except Exception:
        return []


def search_the_muse(keywords: str, location: str, country: str = "United States", num: int = 20) -> List[Dict]:
    """Search The Muse — free, no API key. Quality tech/startup jobs, US-focused."""
    try:
        url = "https://www.themuse.com/api/public/jobs"
        params = {"page": 0, "descending": "true"}

        kw_lower = keywords.lower()
        if any(w in kw_lower for w in ["engineer", "developer", "software", "backend", "frontend", "fullstack", "devops", "sre"]):
            params["category"] = "Software Engineer"
        elif any(w in kw_lower for w in ["data scientist", "machine learning", "ml", "ai"]):
            params["category"] = "Data Science"
        elif any(w in kw_lower for w in ["product manager", "product management"]):
            params["category"] = "Product"
        elif any(w in kw_lower for w in ["design", "ux", "ui"]):
            params["category"] = "Design and UX"
        elif any(w in kw_lower for w in ["market", "growth", "seo", "content"]):
            params["category"] = "Marketing and PR"
        elif any(w in kw_lower for w in ["sales", "account", "business development"]):
            params["category"] = "Sales"

        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        jobs = []
        kw_terms = [k.strip().lower() for k in keywords.split() if len(k.strip()) > 2]

        # US state abbreviations for filtering
        us_states = {
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID",
            "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS",
            "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
            "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV",
            "WI", "WY", "DC",
        }

        def _is_us_location(loc: str) -> bool:
            """Return True if this location string is in the US (or remote/flexible)."""
            if not loc:
                return True  # no location info — include
            l = loc.lower()
            if any(w in l for w in ("remote", "flexible", "united states", " usa", ", usa")):
                return True
            # Match ", ST" at end or before non-letter — avoid false matches like "India" matching "IN"
            return bool(re.search(
                r",\s*(" + "|".join(us_states) + r")\b",
                loc,
                re.IGNORECASE,
            ))

        for j in data.get("results", [])[:num * 4]:
            if len(jobs) >= num:
                break
            title = j.get("name", "")
            company = j.get("company", {}).get("name", "N/A")
            description = j.get("contents", "") or ""
            description = re.sub(r"<[^>]+>", " ", description).strip()
            description = re.sub(r"\s+", " ", description)

            searchable = (title + " " + description[:500]).lower()
            if kw_terms and not any(k in searchable for k in kw_terms):
                continue

            all_locs = j.get("locations", [])
            # Pick first US location if multiple exist; fall back to first location
            loc_str = ""
            for loc_entry in all_locs:
                candidate = loc_entry.get("name", "")
                if country != "United States" or _is_us_location(candidate):
                    loc_str = candidate
                    break
            if not loc_str and all_locs:
                loc_str = all_locs[0].get("name", "")

            # Country filter
            if country == "United States" and not _is_us_location(loc_str):
                continue

            # City filter within country
            if location and location.lower() not in ("remote", "any", "anywhere"):
                loc_city = location.lower().split(",")[0].strip()
                if loc_city and loc_city not in loc_str.lower() and "remote" not in loc_str.lower() and "flexible" not in loc_str.lower():
                    continue

            job_url = j.get("refs", {}).get("landing_page", "")
            posted = j.get("publication_date", "")[:10] if j.get("publication_date") else ""

            jobs.append({
                "title": title,
                "company": company,
                "location": loc_str or location or country,
                "description": description[:2000],
                "url": job_url,
                "salary_min": None,
                "salary_max": None,
                "salary_display": "Not specified",
                "posted_date": posted,
                "source": "The Muse",
                "employment_type": j.get("type", ""),
                "remote": "remote" in (loc_str or "").lower() or "flexible" in (loc_str or "").lower(),
            })

        return jobs
    except Exception:
        return []


def search_serpapi_google_jobs(keywords: str, location: str, country: str = "United States", num: int = 20) -> List[Dict]:
    """
    Search Google Jobs via SerpAPI — aggregates LinkedIn, Indeed, Glassdoor, ZipRecruiter.
    Requires SERPAPI_KEY. Free tier: 100 searches/month at serpapi.com
    """
    api_key = os.getenv("SERPAPI_KEY", "")
    if not api_key:
        return []

    try:
        url = "https://serpapi.com/search"
        query = f"{keywords} {location}".strip() if location else keywords
        params = {
            "engine": "google_jobs",
            "q": query,
            "hl": "en",
            "gl": COUNTRY_CODES.get(country, "us"),
            "api_key": api_key,
        }
        if location and location.lower() not in ("remote", "any", "anywhere"):
            params["location"] = f"{location}, {country}"
        else:
            params["location"] = country

        r = requests.get(url, params=params, timeout=20)
        r.raise_for_status()
        data = r.json()

        jobs = []
        for j in data.get("jobs_results", [])[:num]:
            title = j.get("title", "")
            company = j.get("company_name", "N/A")
            loc_str = j.get("location", location or country)
            description = j.get("description", "")
            posted = j.get("detected_extensions", {}).get("posted_at", "")

            salary_str = j.get("detected_extensions", {}).get("salary", "")
            salary_min, salary_max = _parse_salary_string(salary_str)

            apply_options = j.get("apply_options", [])
            apply_url = ""
            platform = "Google Jobs"
            for opt in apply_options:
                link = opt.get("link", "")
                detected = _detect_source_from_url(link)
                if detected in ("LinkedIn", "Indeed", "Glassdoor", "ZipRecruiter"):
                    apply_url = link
                    platform = detected
                    break
                if not apply_url:
                    apply_url = link
                    platform = opt.get("title", "Google Jobs")

            via = j.get("via", "")
            if via and platform == "Google Jobs":
                platform = via.replace("via ", "")

            jobs.append({
                "title": title,
                "company": company,
                "location": loc_str,
                "description": description,
                "url": apply_url,
                "salary_min": salary_min,
                "salary_max": salary_max,
                "salary_display": _fmt_salary(salary_min, salary_max) if (salary_min or salary_max) else (salary_str or "Not specified"),
                "posted_date": posted,
                "source": f"Google Jobs ({platform})" if platform != "Google Jobs" else "Google Jobs",
                "employment_type": "",
                "remote": j.get("detected_extensions", {}).get("work_from_home", False),
            })

        return jobs
    except Exception:
        return []


def _parse_salary_string(salary_str: str):
    """Parse a salary string like '$120K–$160K a year' into (min, max) ints."""
    if not salary_str:
        return None, None
    nums = re.findall(r"[\d,]+\.?\d*", salary_str.replace("K", "000").replace("k", "000"))
    nums = [int(float(n.replace(",", ""))) for n in nums if n]
    if len(nums) >= 2:
        return nums[0], nums[1]
    if len(nums) == 1:
        return nums[0], None
    return None, None


def search_jobs(keywords: str, location: str = "", country: str = "United States", num: int = 20) -> List[Dict]:
    """
    Aggregate jobs from all configured sources, scoped to the given country.

    Free sources (no key needed): The Muse, RemoteOK
    Paid/key sources: SerpAPI (Google Jobs/LinkedIn/Indeed), JSearch (RapidAPI), Adzuna
    """
    country_code = COUNTRY_CODES.get(country, "us")
    all_jobs = (
        search_serpapi_google_jobs(keywords, location, country=country, num=num)
        + search_jsearch(keywords, location, country=country, num=num)
        + search_adzuna(keywords, location, country_code=country_code, num=num)
        + search_the_muse(keywords, location, country=country, num=num)
        + search_remoteok(keywords, num=num)
    )

    seen, unique = set(), []
    for job in all_jobs:
        key = (job["title"].lower().strip(), job["company"].lower().strip())
        if key not in seen and job["title"] and job["company"]:
            seen.add(key)
            unique.append(job)
    return unique


def get_active_sources() -> list[str]:
    """Return list of source names that are currently configured/available."""
    sources = ["The Muse (free)", "RemoteOK (free)"]
    if os.getenv("SERPAPI_KEY"):
        sources.insert(0, "Google Jobs/LinkedIn/Indeed (SerpAPI)")
    if os.getenv("RAPIDAPI_KEY"):
        sources.insert(0, "JSearch / LinkedIn / Indeed (RapidAPI)")
    if os.getenv("ADZUNA_APP_ID") and os.getenv("ADZUNA_API_KEY"):
        sources.append("Adzuna")
    return sources


def _fmt_salary(low, high) -> str:
    if low and high:
        return f"${int(low):,} – ${int(high):,}"
    if low:
        return f"${int(low):,}+"
    if high:
        return f"Up to ${int(high):,}"
    return "Not specified"
