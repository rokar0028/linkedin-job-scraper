import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime

# Google API scopes
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Authenticate
credentials = Credentials.from_service_account_file(
    "credentials.json",
    scopes=SCOPES
)

client = gspread.authorize(credentials)

# Open the spreadsheet
sheet = client.open("LinkedIn Job Scraper").sheet1


def append_jobs(jobs):
    """
    Appends only NEW jobs to the Google Sheet.

    Args:
        jobs: List of job dictionaries.

    Returns:
        int: Number of new rows inserted.
    """

    if not jobs:
        return 0

    # -----------------------------------
    # Read existing Job URLs
    # -----------------------------------
    existing_urls = set()

    existing_rows = sheet.get_all_values()[1:]  # Skip the first header row

    for row in existing_rows:
        if len(row) >= 4:
            existing_urls.add(row[3].strip())

    # -----------------------------------
    # Keep only NEW jobs
    # -----------------------------------
    rows_to_insert = []

    for job in jobs:

        if job["job_url"] in existing_urls:
            continue

        rows_to_insert.append([
            job["title"],
            job["company"],
            job["location"],
            job["job_url"]
        ])

        existing_urls.add(job["job_url"])

    # -----------------------------------
    # Nothing new to insert
    # -----------------------------------
    if not rows_to_insert:
        return 0

    # -----------------------------------
    # Create Scrape Run separator
    # -----------------------------------
    timestamp = datetime.now().strftime("%d %b %Y | %I:%M %p")

    separator_row = [
        f"──────── Scrape Run : {timestamp} ────────",
        "",
        "",
        ""
    ]

    header_row = [
        "Title",
        "Company",
        "Location",
        "Job URL"
    ]

    # -----------------------------------
    # Insert into Google Sheet
    # -----------------------------------

    # Blank line between scrape sessions
    sheet.append_row(["", "", "", ""])

    # Scrape Run separator
    sheet.append_row(separator_row)

    # Column headers
    sheet.append_row(header_row)

    # Job data
    sheet.append_rows(rows_to_insert)

    return len(rows_to_insert)
