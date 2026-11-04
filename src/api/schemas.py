from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class ScrapeRequest(BaseModel):
    job_title: str = Field(..., example="AI Engineer", description="Job title keyword to search")
    location: Optional[str] = Field("", example="San Francisco, CA", description="Target location")
    remote: Optional[str] = Field("no", example="yes", description="'yes' to filter remote roles, 'no' otherwise")
    max_jobs: Optional[int] = Field(None, example=30, description="Max jobs to scrape (defaults to server config)")


class ScrapeResponse(BaseModel):
    status: str
    jobs_scraped: int
    jobs_inserted: int
    duplicates_skipped: int
    jobs: Optional[List[Dict[str, Any]]] = None


class AsyncTaskResponse(BaseModel):
    message: str
    task_id: str
    status_check_url: str


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    request: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
