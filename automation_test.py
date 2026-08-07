import os
import json
from playwright.sync_api import sync_playwright


def automate_search(job_title, location):
    """
    Opens LinkedIn, searches for jobs,
    applies location and Remote filter,
    then returns the Playwright objects.
    """

    # -----------------------------------
    # Create auth.json from Render secret
    # -----------------------------------
    if not os.path.exists("auth.json"):
        auth_data = os.getenv("LINKEDIN_AUTH")

        if not auth_data:
            raise ValueError(
                "No auth.json found and LINKEDIN_AUTH environment variable is not set."
            )

        with open("auth.json", "w", encoding="utf-8") as f:
            json.dump(json.loads(auth_data), f)

    playwright = sync_playwright().start()

    # Launch Browser
    browser = playwright.chromium.launch(
        headless=True
    )

    # Load LinkedIn Login Session
    context = browser.new_context(storage_state="auth.json")
    page = context.new_page()

    # Open LinkedIn Jobs
    page.goto("https://www.linkedin.com/jobs/")
    page.wait_for_timeout(5000)

    # Search Job Title
    search_box = page.locator('[data-testid="typeahead-input"]')
    search_box.click()
    search_box.fill(job_title)
    search_box.press("Enter")

    page.wait_for_timeout(3000)

    # Open Location Filter
    location_chip = page.locator('[aria-label^="Location"]')
    location_chip.click()

    page.wait_for_timeout(1000)

    # Change Location
    location_box = page.locator('[aria-label="Location"]')
    location_box.click()

    location_box.press("Control+A")
    location_box.press("Backspace")

    location_box.type(location)

    # Wait for suggestions
    page.wait_for_timeout(3000)

    # Select first suggestion
    page.locator("#semanticSearchBoxLocationList a").first.click()

    # Wait for search results
    page.wait_for_timeout(5000)

    # Apply Remote Filter
    remote_filter = page.locator(
        '[role="radio"][aria-label="Filter by Remote"]'
    )

    remote_filter.first.click()

    # Wait for filtered results
    page.wait_for_timeout(5000)

    # Return everything main.py will need
    return playwright, browser, page