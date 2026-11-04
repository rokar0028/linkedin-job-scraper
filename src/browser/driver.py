import os
import json
import urllib.parse
from typing import Tuple, Optional
from playwright.sync_api import sync_playwright, Playwright, Browser, Page
from src.core.config import settings


def get_auth_storage_state() -> str:
    """
    Ensures authentication credentials exist either as a local file
    or generated from the LINKEDIN_AUTH environment variable.
    """
    if os.path.exists(settings.LINKEDIN_AUTH_FILE):
        return settings.LINKEDIN_AUTH_FILE

    if settings.LINKEDIN_AUTH_ENV:
        auth_data = settings.LINKEDIN_AUTH_ENV.strip()
        with open(settings.LINKEDIN_AUTH_FILE, "w", encoding="utf-8") as f:
            json.dump(json.loads(auth_data), f)
        return settings.LINKEDIN_AUTH_FILE

    raise FileNotFoundError(
        f"Missing session file '{settings.LINKEDIN_AUTH_FILE}' and LINKEDIN_AUTH environment variable is not set.\n"
        f"Run 'python scripts/login.py' locally to generate '{settings.LINKEDIN_AUTH_FILE}' first."
    )


# Filter Code Mappings for LinkedIn URL parameters
DATE_POSTED_MAP = {
    "past_24h": "r86400",
    "24h": "r86400",
    "day": "r86400",
    "past_week": "r604800",
    "week": "r604800",
    "past_month": "r2592000",
    "month": "r2592000",
}

EXP_LEVEL_MAP = {
    "internship": "1",
    "entry": "2",
    "entry_level": "2",
    "associate": "3",
    "mid_senior": "4",
    "mid": "4",
    "director": "5",
    "executive": "6",
}


def build_search_url(
    job_title: str,
    location: str = "",
    remote: str = "no",
    date_posted: Optional[str] = None,
    experience_level: Optional[str] = None
) -> str:
    """
    Builds a direct LinkedIn jobs search URL with query parameters.
    - f_WT=2: Remote
    - f_TPR: Date posted (r86400=24h, r604800=week, r2592000=month)
    - f_E: Experience level (1=intern, 2=entry, 3=associate, 4=mid-senior)
    """
    base_url = "https://www.linkedin.com/jobs/search/?"
    params = {}

    if job_title and job_title.strip():
        params["keywords"] = job_title.strip()

    if location and location.strip():
        params["location"] = location.strip()

    # Remote filter
    if remote and str(remote).strip().lower() in ("yes", "true", "1", "y"):
        params["f_WT"] = "2"

    # Date posted filter
    if date_posted:
        key = str(date_posted).strip().lower()
        if key in DATE_POSTED_MAP:
            params["f_TPR"] = DATE_POSTED_MAP[key]

    # Experience level filter
    if experience_level:
        key = str(experience_level).strip().lower()
        if key in EXP_LEVEL_MAP:
            params["f_E"] = EXP_LEVEL_MAP[key]

    return base_url + urllib.parse.urlencode(params)


def automate_search(
    job_title: str,
    location: str = "",
    remote: str = "no",
    date_posted: Optional[str] = None,
    experience_level: Optional[str] = None
) -> Tuple[Playwright, Browser, Page]:
    """
    Launches Playwright Chromium session and navigates directly to the filtered
    LinkedIn jobs search page using query parameters for maximum speed and resilience.
    Guarantees browser cleanup if setup fails.
    """
    auth_state_path = get_auth_storage_state()

    playwright = sync_playwright().start()
    browser = None

    try:
        browser_args = [
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--disable-dev-shm-usage",
            "--disable-blink-features=AutomationControlled",
        ]

        browser = playwright.chromium.launch(
            headless=settings.HEADLESS,
            args=browser_args
        )

        context = browser.new_context(
            storage_state=auth_state_path,
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        search_url = build_search_url(
            job_title=job_title,
            location=location,
            remote=remote,
            date_posted=date_posted,
            experience_level=experience_level
        )
        print(f"[*] Navigating to search URL (Headless: {settings.HEADLESS})...")
        print(f"    URL: {search_url}")

        page.goto(search_url, wait_until="domcontentloaded", timeout=settings.DEFAULT_TIMEOUT * 3)

        # Wait for page to settle
        page.wait_for_timeout(3000)

        # Check for potential auth redirect or checkpoint
        current_url = page.url
        if "checkpoint" in current_url or "login" in current_url:
            raise PermissionError(
                f"LinkedIn session challenge or login required. Current URL: {current_url}"
            )

        print(f"[*] Search page loaded: '{page.title()}'")
        return playwright, browser, page

    except Exception as e:
        print(f"[!] Error during automate_search: {e}")
        if browser:
            try:
                browser.close()
            except Exception:
                pass
        try:
            playwright.stop()
        except Exception:
            pass
        raise
