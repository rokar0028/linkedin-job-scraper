"""
Root CLI entrypoint for LinkedIn Job Scraper.
Delegates orchestration to src.pipeline.
"""
import sys
from src.pipeline import run_scraper
from src.core.config import settings


def main():
    print("========================================")
    print("      LinkedIn Job Scraper CLI          ")
    print("========================================")

    job_title = input("Enter Job Title [e.g. Software Engineer]: ").strip()
    if not job_title:
        print("[!] Job title is required.")
        sys.exit(1)

    location = input("Enter Location [e.g. United States or San Francisco]: ").strip()

    while True:
        remote = input("Filter for Remote only? (yes/no) [no]: ").strip().lower()
        if not remote:
            remote = "no"
            break
        if remote in ["yes", "no", "y", "n"]:
            remote = "yes" if remote in ["yes", "y"] else "no"
            break
        print("Please enter 'yes' or 'no'.")

    max_jobs_input = input(f"Max jobs to scrape [{settings.MAX_JOBS}]: ").strip()
    max_jobs = int(max_jobs_input) if max_jobs_input.isdigit() else settings.MAX_JOBS

    result = run_scraper(job_title, location, remote, max_jobs=max_jobs)
    print("\nResult Summary:", {k: v for k, v in result.items() if k != "jobs"})


if __name__ == "__main__":
    main()
