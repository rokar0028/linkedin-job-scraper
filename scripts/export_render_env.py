import json
import os
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent

auth_path = root_dir / "auth.json"
creds_path = root_dir / "credentials.json"

print("=" * 60)
print(" RENDER ENVIRONMENT VARIABLE HELPER")
print("=" * 60)
print("Copy the values below into your Render Dashboard under:")
print("Environment > Environment Variables\n")

print("-" * 60)
print("1. Key: HEADLESS")
print("   Value: true")

if creds_path.exists():
    try:
        creds_content = json.dumps(json.loads(creds_path.read_text(encoding="utf-8")))
        print("\n" + "-" * 60)
        print("2. Key: GOOGLE_CREDENTIALS")
        print("   Value (compact JSON):")
        print(creds_content)
    except Exception as e:
        print(f"\n[!] Error parsing credentials.json: {e}")
else:
    print("\n[!] credentials.json not found.")

if auth_path.exists():
    try:
        auth_content = json.dumps(json.loads(auth_path.read_text(encoding="utf-8")))
        print("\n" + "-" * 60)
        print("3. Key: LINKEDIN_AUTH")
        print("   Value (compact JSON):")
        print(auth_content)
    except Exception as e:
        print(f"\n[!] Error parsing auth.json: {e}")
else:
    print("\n[!] auth.json not found.")

print("\n" + "-" * 60)
print("4. Key: GOOGLE_SHEET_NAME")
print("   Value: LinkedIn Job Scraper")
print("=" * 60)
