from automation_test import automate_search
from scraper import scrape_jobs
from sheets import append_jobs


def main():
    # -----------------------------
    # User Inputs
    # -----------------------------
    job_title = input("Enter Job Title: ")
    location = input("Enter Location: ")

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

    except Exception as e:
        print(f"\nError: {e}")

    finally:
        input("\nPress Enter to close the browser...")

        browser.close()
        playwright.stop()


if __name__ == "__main__":
    main()