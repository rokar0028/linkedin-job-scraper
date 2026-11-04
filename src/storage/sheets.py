import os
import json
from datetime import datetime
from typing import List, Dict, Any
import gspread
from google.oauth2.service_account import Credentials
from src.core.config import settings

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

DEFAULT_HEADERS = [
    "Scraped At",
    "Search Query",
    "Title",
    "Company",
    "Location",
    "Job URL"
]


def get_sheets_client() -> gspread.Client:
    """
    Authenticates with Google Sheets API using service account credentials
    from GOOGLE_CREDENTIALS env var or credentials.json file.
    """
    credentials_json = settings.GOOGLE_CREDS_ENV

    if credentials_json:
        creds = Credentials.from_service_account_info(
            json.loads(credentials_json.strip()),
            scopes=SCOPES
        )
    elif os.path.exists(settings.GOOGLE_CREDS_FILE):
        creds = Credentials.from_service_account_file(
            settings.GOOGLE_CREDS_FILE,
            scopes=SCOPES
        )
    else:
        raise FileNotFoundError(
            f"Google credentials not found. Set GOOGLE_CREDENTIALS environment variable "
            f"or place '{settings.GOOGLE_CREDS_FILE}' in the project directory."
        )

    return gspread.authorize(creds)


def get_or_create_sheet(client: gspread.Client, sheet_name: str = None) -> gspread.Worksheet:
    """
    Opens the spreadsheet and sheet1, ensuring base headers exist if completely empty.
    """
    name = sheet_name or settings.GOOGLE_SHEET_NAME
    spreadsheet = client.open(name)
    sheet = spreadsheet.sheet1

    first_row = sheet.row_values(1)
    if not first_row:
        sheet.append_row(DEFAULT_HEADERS)

    return sheet


def detect_sheet_schema(sheet: gspread.Worksheet):
    """
    Detects whether the sheet is using legacy 4-column format [Title, Company, Location, URL]
    or modern 6-column format [Timestamp, Query, Title, Company, Location, URL].
    Returns (url_col_idx, is_legacy).
    """
    # Check column 4 vs column 6
    try:
        col4_values = sheet.col_values(4)
        has_urls_in_col4 = any("linkedin.com/jobs/view/" in v for v in col4_values[:30])
        has_url_header_col4 = any("url" in v.lower() for v in col4_values[:5])
        if has_urls_in_col4 or has_url_header_col4:
            return 4, True
    except Exception:
        pass

    try:
        col6_values = sheet.col_values(6)
        has_urls_in_col6 = any("linkedin.com/jobs/view/" in v for v in col6_values[:30])
        has_url_header_col6 = any("url" in v.lower() for v in col6_values[:5])
        if has_urls_in_col6 or has_url_header_col6:
            return 6, False
    except Exception:
        pass

    # Default to 6 columns for new sheets
    return 6, False


def append_jobs(jobs: List[Dict[str, str]], search_query: str = "") -> Dict[str, int]:
    """
    Appends only NEW jobs to the Google Sheet in a single batched API call.
    Automatically matches existing sheet schema (4-column legacy or 6-column modern).
    """
    if not jobs:
        print("[*] No jobs to append.")
        return {"inserted": 0, "duplicates": 0, "total": 0}

    try:
        client = get_sheets_client()
        sheet = get_or_create_sheet(client)
    except Exception as e:
        print(f"[!] Google Sheets connection failed: {e}")
        raise

    url_col_idx, is_legacy_schema = detect_sheet_schema(sheet)

    # Efficiently load all existing URLs from the identified URL column
    try:
        raw_col = sheet.col_values(url_col_idx)
        existing_urls = set(u.strip() for u in raw_col if "linkedin.com/jobs/view/" in u)
    except Exception:
        existing_urls = set()
        for row in sheet.get_all_values():
            for cell in row:
                if "linkedin.com/jobs/view/" in cell:
                    existing_urls.add(cell.strip())

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows_to_insert = []
    duplicates = 0

    for job in jobs:
        url = job.get("job_url", "").strip()
        if not url or url in existing_urls:
            duplicates += 1
            continue

        existing_urls.add(url)

        if is_legacy_schema:
            rows_to_insert.append([
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
                url
            ])
        else:
            rows_to_insert.append([
                timestamp,
                search_query,
                job.get("title", ""),
                job.get("company", ""),
                job.get("location", ""),
                url
            ])

    if rows_to_insert:
        sheet.append_rows(rows_to_insert)
        print(f"[+] Appended {len(rows_to_insert)} new jobs to Google Sheet '{settings.GOOGLE_SHEET_NAME}'.")
    else:
        print(f"[*] All {len(jobs)} scraped jobs are already present in the sheet (0 new).")

    return {
        "inserted": len(rows_to_insert),
        "duplicates": duplicates,
        "total": len(jobs)
    }
