import sys
from pathlib import Path

# Add project root to sys.path so 'src' can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.storage.sheets import get_sheets_client, get_or_create_sheet
from src.core.config import settings


def test_connection():
    print(f"[*] Testing Google Sheets connection to '{settings.GOOGLE_SHEET_NAME}'...")
    try:
        client = get_sheets_client()
        sheet = get_or_create_sheet(client)
        title = sheet.title
        rows = len(sheet.get_all_values())
        print(f"[OK] Successfully connected to sheet: '{title}' (Total rows: {rows})")
    except Exception as e:
        print(f"[!] Google Sheets connection failed: {e}")


if __name__ == "__main__":
    test_connection()
