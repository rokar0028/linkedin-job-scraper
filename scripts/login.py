import sys
from pathlib import Path

# Add project root to sys.path so 'src' can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from playwright.sync_api import sync_playwright
from src.core.config import settings


def login_and_save_session():
    """
    Launches a visible Chromium browser to allow the user to log in to LinkedIn manually.
    Saves the session storage state (cookies, local storage) to auth.json for automated reuse.
    """
    print("\n" + "=" * 60)
    print(" LinkedIn Authentication Session Generator")
    print("=" * 60)
    print("1. A browser window will open to LinkedIn's login page.")
    print("2. Enter your credentials, complete 2FA/CAPTCHA if prompted.")
    print("3. Once your LinkedIn feed is visible, return here and press Enter.\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        )
        page = context.new_page()

        page.goto("https://www.linkedin.com/login")

        input(">>> Log in completely until you see your feed, then press Enter here... ")

        context.storage_state(path=settings.LINKEDIN_AUTH_FILE)
        browser.close()

    print(f"\n[OK] Login session successfully saved to '{settings.LINKEDIN_AUTH_FILE}'!")
    print("\n--- Cloud Deployment Tip (Render/Heroku) ---")
    print("To run on Render without committing auth.json:")
    print("1. Open auth.json and copy its entire text.")
    print("2. In your Render Dashboard, add an Environment Variable:")
    print("   Name:  LINKEDIN_AUTH")
    print("   Value: <paste the JSON content>")
    print("=" * 60)


if __name__ == "__main__":
    login_and_save_session()
