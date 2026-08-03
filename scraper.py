import re


def scrape_jobs(page, max_jobs=50, debug=False):
    """
    Scrapes LinkedIn job cards from the already-open page.

    Args:
        page: Playwright page object already filtered to the correct results.
        max_jobs: Maximum number of unique jobs to collect.
        debug: If True, prints detailed diagnostic information.

    Returns:
        List[dict]: job records with title, company, location, and job_url
    """
    jobs = []

    # Wait for search results to load
    page.wait_for_timeout(5000)

    if debug:
        print("Current URL :", page.url)
        print("Page title  :", page.title())

        # Save HTML for debugging
        with open("linkedin.html", "w", encoding="utf-8") as f:
            f.write(page.content())

        print("\nHTML saved successfully.")

    # Locate all job cards
    job_cards = page.locator('[componentkey^="job-card-component-ref-"]')
    total_cards = job_cards.count()

    if debug:
        print(f"\nTotal Job Cards Found: {total_cards}")

    seen = set()

    for i in range(total_cards):
        if len(jobs) >= max_jobs:
            break

        card = job_cards.nth(i)

        try:
            # Extract job ID from componentkey
            component_key = card.get_attribute("componentkey")
            if not component_key:
                continue

            match = re.search(r"(\d+)$", component_key)
            if not match:
                continue

            job_id = match.group(1)

            paragraphs = card.locator("p")
            if paragraphs.count() < 3:
                continue

            # Extract title
            title = (
                paragraphs.nth(0)
                .locator("span[aria-hidden='true']")
                .first
                .inner_text()
                .strip()
            )

            company = paragraphs.nth(1).inner_text().strip()
            location = paragraphs.nth(2).inner_text().strip()

            # Diagnostic block for blank titles
            if title == "":
                if debug:
                    print("\n" + "=" * 80)
                    print("BLANK TITLE FOUND")
                    print("=" * 80)
                    print(f"Card Index    : {i}")
                    print(f"Job ID        : {job_id}")
                    print(f"Company       : {company}")
                    print(f"Location      : {location}")
                    print(f"Component Key : {component_key}")

                    print("\n----- CARD INNER HTML -----\n")
                    print(card.inner_html())

                    print("\n----- FIRST <p> INNER HTML -----\n")
                    print(paragraphs.nth(0).inner_html())

                    print("\n----- FIRST <p> INNER TEXT -----\n")
                    print(paragraphs.nth(0).inner_text())

                continue

        except Exception as e:
            if debug:
                print(f"Skipping card {i}: {e}")
            continue

        # Skip duplicates
        unique_key = (job_id, company)
        if unique_key in seen:
            continue

        seen.add(unique_key)

        job_url = f"https://www.linkedin.com/jobs/view/{job_id}/"

        jobs.append(
            {
                "title": title,
                "company": company,
                "location": location,
                "job_url": job_url,
            }
        )

    return jobs