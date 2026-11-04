import re
import time
from typing import List, Dict, Optional
from playwright.sync_api import Page, Locator
from src.core.config import settings


def extract_title(card: Locator, paragraphs: Locator) -> str:
    """
    Extracts the job title using multi-strategy fallbacks supporting both
    LinkedIn SPA and Search Results templates.
    """
    # Strategy 1: Anchor link with /jobs/view/ (Universal)
    try:
        link = card.locator('a[href*="/jobs/view/"]').first
        if link.count() > 0:
            text = link.inner_text().strip()
            if text:
                return text.split("\n")[0].strip()
    except Exception:
        pass

    # Strategy 2: Visible text in the first paragraph's aria-hidden span (SPA template)
    try:
        if paragraphs.count() > 0:
            title_span = paragraphs.nth(0).locator("span[aria-hidden='true']").first
            if title_span.is_visible():
                title = title_span.inner_text().strip()
                if title:
                    return title
    except Exception:
        pass

    # Strategy 3: Cleaned accessible text from first paragraph
    try:
        if paragraphs.count() > 0:
            raw_p = paragraphs.nth(0).inner_text().strip()
            cleaned_p = re.sub(r"\s*\(Verified job\)", "", raw_p, flags=re.I).strip()
            if cleaned_p:
                return cleaned_p.split("\n")[0].strip()
    except Exception:
        pass

    # Strategy 4: Dismiss button aria-label
    try:
        dismiss_btn = card.locator('button[aria-label*="Dismiss"]').first
        if dismiss_btn.count() > 0:
            aria_label = dismiss_btn.get_attribute("aria-label") or ""
            match = re.search(r"Dismiss\s+(.*?)\s+job", aria_label, flags=re.I)
            if match and match.group(1).strip():
                return match.group(1).strip()
    except Exception:
        pass

    return ""


def extract_job_id(card: Locator) -> Optional[str]:
    """
    Extracts the numeric job ID from anchor href, componentkey, or data attributes.
    """
    # 1. From anchor href (matches both template variants)
    try:
        link = card.locator('a[href*="/jobs/view/"]').first
        if link.count() > 0:
            href = link.get_attribute("href") or ""
            match = re.search(r"(\d{8,})", href)
            if match:
                return match.group(1)
    except Exception:
        pass

    # 2. From componentkey attribute
    try:
        component_key = card.get_attribute("componentkey")
        if component_key:
            match = re.search(r"(\d+)$", component_key)
            if match:
                return match.group(1)
    except Exception:
        pass

    # 3. From data-occludable-job-id or data-job-id attribute
    for attr in ("data-occludable-job-id", "data-job-id", "data-entity-urn"):
        try:
            val = card.get_attribute(attr)
            if val:
                match = re.search(r"(\d{8,})", val)
                if match:
                    return match.group(1)
        except Exception:
            pass

    return None


def extract_company(card: Locator, paragraphs: Locator) -> str:
    """
    Extracts the company name supporting both templates.
    """
    try:
        comp_elem = card.locator('.base-search-card__subtitle, [class*="subtitle"], [class*="company-name"]').first
        if comp_elem.count() > 0:
            text = comp_elem.inner_text().strip()
            if text:
                return text.split("\n")[0].strip()
    except Exception:
        pass

    if paragraphs.count() >= 2:
        return paragraphs.nth(1).inner_text().strip()

    return "Unknown"


def extract_location(card: Locator, paragraphs: Locator) -> str:
    """
    Extracts the job location supporting both templates.
    """
    try:
        loc_elem = card.locator('.job-search-card__location, [class*="job-search-card__location"], [class*="location"]').first
        if loc_elem.count() > 0:
            text = loc_elem.inner_text().strip()
            if text:
                return text.split("\n")[0].strip()
    except Exception:
        pass

    if paragraphs.count() >= 3:
        return paragraphs.nth(2).inner_text().strip()

    return "Remote/Unspecified"


def scrape_jobs(
    page: Page,
    max_jobs: Optional[int] = None,
    debug: bool = False
) -> List[Dict[str, str]]:
    """
    Scrapes LinkedIn job cards with universal dual-template support and auto-scrolling.
    """
    limit = max_jobs if max_jobs is not None else settings.MAX_JOBS

    jobs: List[Dict[str, str]] = []
    seen_ids = set()

    # Wait for either template's card selector to render
    card_selector = (
        '[componentkey^="job-card-component-ref-"], '
        '.base-card, .job-search-card, '
        'li:has(a[href*="/jobs/view/"]), '
        '.jobs-search-results-list'
    )

    try:
        page.wait_for_selector(card_selector, timeout=settings.DEFAULT_TIMEOUT)
    except Exception:
        print("[*] Proceeding with DOM scan...")

    # Identify scrollable container or fallback to window
    scroll_container = page.locator(".jobs-search-results-list, .scaffold-layout__list, .jobs-search__results-list").first

    last_card_count = 0
    stagnant_scroll_attempts = 0
    max_scroll_attempts = 15

    print(f"[*] Extracting up to {limit} jobs...")

    while len(jobs) < limit and stagnant_scroll_attempts < max_scroll_attempts:
        card_locators = page.locator(
            '[componentkey^="job-card-component-ref-"], .base-card, .job-search-card, li:has(a[href*="/jobs/view/"])'
        )
        total_cards = card_locators.count()

        for i in range(total_cards):
            if len(jobs) >= limit:
                break

            card = card_locators.nth(i)

            try:
                job_id = extract_job_id(card)
                if not job_id or job_id in seen_ids:
                    continue

                paragraphs = card.locator("p")
                title = extract_title(card, paragraphs)
                if not title:
                    continue

                company = extract_company(card, paragraphs)
                location = extract_location(card, paragraphs)
                job_url = f"https://www.linkedin.com/jobs/view/{job_id}/"

                seen_ids.add(job_id)
                jobs.append({
                    "job_id": job_id,
                    "title": title,
                    "company": company,
                    "location": location,
                    "job_url": job_url
                })

                if debug:
                    print(f"  [{len(jobs)}/{limit}] {title} @ {company} ({location})")

            except Exception as e:
                if debug:
                    print(f"  [!] Skipped card {i}: {e}")
                continue

        if len(jobs) >= limit:
            break

        if total_cards == last_card_count:
            stagnant_scroll_attempts += 1
        else:
            stagnant_scroll_attempts = 0
            last_card_count = total_cards

        # Scroll to load next batch
        try:
            if scroll_container.count() > 0 and scroll_container.is_visible():
                scroll_container.evaluate("el => el.scrollBy(0, 1000)")
            else:
                page.evaluate("window.scrollBy(0, 1000)")
            time.sleep(1.0)
        except Exception:
            break

    print(f"[+] Total unique jobs extracted: {len(jobs)}")
    return jobs
