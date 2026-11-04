"""
Backward-compatibility alias for src.scraper.engine.
"""
from src.scraper.engine import scrape_jobs, extract_title, extract_job_id

__all__ = ["scrape_jobs", "extract_title", "extract_job_id"]
