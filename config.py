"""
Backward-compatibility alias for src.core.config.
"""
from src.core.config import settings

HEADLESS = settings.HEADLESS
BROWSER = settings.BROWSER
TIMEOUT = settings.DEFAULT_TIMEOUT
MAX_JOBS = settings.MAX_JOBS
LINKEDIN_AUTH_FILE = settings.LINKEDIN_AUTH_FILE
LINKEDIN_AUTH_ENV = settings.LINKEDIN_AUTH_ENV
GOOGLE_SHEET_NAME = settings.GOOGLE_SHEET_NAME
GOOGLE_CREDS_FILE = settings.GOOGLE_CREDS_FILE
GOOGLE_CREDS_ENV = settings.GOOGLE_CREDS_ENV

__all__ = [
    "settings",
    "HEADLESS",
    "BROWSER",
    "TIMEOUT",
    "MAX_JOBS",
    "LINKEDIN_AUTH_FILE",
    "LINKEDIN_AUTH_ENV",
    "GOOGLE_SHEET_NAME",
    "GOOGLE_CREDS_FILE",
    "GOOGLE_CREDS_ENV"
]
