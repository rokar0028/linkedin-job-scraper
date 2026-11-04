from typing import Optional, Dict, Any
from src.browser.driver import automate_search
from src.scraper.engine import scrape_jobs
from src.storage.sheets import append_jobs
from src.core.config import settings


def run_scraper(
    job_title: str,
    location: str = "",
    remote: str = "no",
    date_posted: Optional[str] = None,
    experience_level: Optional[str] = None,
    max_jobs: Optional[int] = None
) -> Dict[str, Any]:
    """
    Executes the end-to-end scraper pipeline:
    1. Launches browser & navigates with search/filters (Remote, Date Posted, Experience Level).
    2. Extracts jobs up to max_jobs with container auto-scrolling.
    3. Syncs new unique jobs to Google Sheets.
    4. Guarantees browser shutdown.
    """
    limit = max_jobs if max_jobs is not None else settings.MAX_JOBS

    filter_info = []
    if remote and str(remote).lower() in ("yes", "y", "true", "1"):
        filter_info.append("Remote: yes")
    if date_posted:
        filter_info.append(f"Date: {date_posted}")
    if experience_level:
        filter_info.append(f"Exp: {experience_level}")

    filter_summary = ", ".join(filter_info) if filter_info else "No extra filters"

    print(f"\n{'=' * 60}")
    print(f" Starting LinkedIn Scraper Pipeline")
    print(f" Title: '{job_title}' | Location: '{location}' | Filters: [{filter_summary}] | Limit: {limit}")
    print(f"{'=' * 60}")

    playwright, browser, page = automate_search(
        job_title=job_title,
        location=location,
        remote=remote,
        date_posted=date_posted,
        experience_level=experience_level
    )

    try:
        # Scrape jobs from results page
        jobs = scrape_jobs(page, max_jobs=limit)

        # Upload to Google Sheets
        search_summary = f"{job_title} | {location} ({filter_summary})"
        sync_result = append_jobs(jobs, search_query=search_summary)

        result = {
            "status": "success",
            "jobs_scraped": len(jobs),
            "jobs_inserted": sync_result["inserted"],
            "duplicates_skipped": sync_result["duplicates"],
            "jobs": jobs
        }

        print(f"\n[OK] Pipeline completed successfully!")
        print(f"    - Jobs Extracted : {len(jobs)}")
        print(f"    - New Inserted   : {sync_result['inserted']}")
        print(f"    - Duplicates     : {sync_result['duplicates']}")

        return result

    except Exception as e:
        print(f"\n[!] Pipeline execution error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        try:
            browser.close()
        except Exception:
            pass
        try:
            playwright.stop()
        except Exception:
            pass
