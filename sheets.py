"""
Backward-compatibility alias for src.storage.sheets.
"""
from src.storage.sheets import append_jobs, get_sheets_client

__all__ = ["append_jobs", "get_sheets_client"]
