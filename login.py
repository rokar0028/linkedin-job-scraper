from playwright.sync_api import sync_playwright


with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)

    context = browser.new_context()

    page = context.new_page()

    page.goto("https://www.linkedin.com/login")

    input("Log into LinkedIn completely, then press Enter here...")

    context.storage_state(path="auth.json")

    print("✅ Login session saved as auth.json")

    browser.close()