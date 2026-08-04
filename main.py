from automation_test import automate_search
from scraper import scrape_jobs
from sheets import append_jobs


def run_scraper(job_title, location):
    # -----------------------------
    # Launch LinkedIn & Apply Filters
    # -----------------------------
    playwright, browser, page = automate_search(
        job_title,
        location
    )

    try:
        # -----------------------------
        # Scrape Jobs
        # -----------------------------
        jobs = scrape_jobs(page)

        # -----------------------------
        # Upload to Google Sheets
        # -----------------------------
        append_jobs(jobs)

        print(f"\nTotal Jobs Scraped: {len(jobs)}")

        return {
            "status": "success",
            "jobs_scraped": len(jobs)
        }

    except Exception as e:
        print(f"\nError: {e}")

        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        browser.close()
        playwright.stop()


def main():
    # -----------------------------
    # User Inputs
    # -----------------------------
    job_title = input("Enter Job Title: ")
    location = input("Enter Location: ")

    result = run_scraper(job_title, location)

    print(result)


if __name__ == "__main__":
    main()