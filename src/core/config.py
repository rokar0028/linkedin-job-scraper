import os
from dataclasses import dataclass
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()


@dataclass(frozen=True)
class Settings:
    # Cloud environment detection (Render, CI, etc.)
    IS_CLOUD: bool = bool(os.getenv("RENDER") or os.getenv("CI"))

    # Browser settings
    HEADLESS: bool = os.getenv("HEADLESS", "true" if bool(os.getenv("RENDER") or os.getenv("CI")) else "false").lower() in ("true", "1", "yes")
    BROWSER: str = os.getenv("BROWSER", "chromium")
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "10000"))

    # Scraper settings
    MAX_JOBS: int = int(os.getenv("MAX_JOBS", "50"))

    # Authentication
    LINKEDIN_AUTH_FILE: str = os.getenv("LINKEDIN_AUTH_FILE", "auth.json")
    LINKEDIN_AUTH_ENV: str = os.getenv("LINKEDIN_AUTH", "")

    # Google Sheets Storage
    GOOGLE_SHEET_NAME: str = os.getenv("GOOGLE_SHEET_NAME", "LinkedIn Job Scraper")
    GOOGLE_CREDS_FILE: str = os.getenv("GOOGLE_CREDS_FILE", "credentials.json")
    GOOGLE_CREDS_ENV: str = os.getenv("GOOGLE_CREDENTIALS", "")


settings = Settings()
