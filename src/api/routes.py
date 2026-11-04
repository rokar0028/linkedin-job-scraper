import uuid
from typing import Dict, Any, Optional
from fastapi import FastAPI, BackgroundTasks, HTTPException, status
from src.api.schemas import ScrapeRequest, AsyncTaskResponse, TaskStatusResponse
from src.pipeline import run_scraper
from src.core.config import settings

app = FastAPI(
    title="LinkedIn Job Scraper API",
    description="Automated Playwright-based LinkedIn Job Scraper syncing to Google Sheets.",
    version="2.1.0"
)

# In-memory store for async background tasks
tasks_db: Dict[str, Dict[str, Any]] = {}


def background_scrape_worker(
    task_id: str,
    job_title: str,
    location: str,
    remote: str,
    date_posted: Optional[str],
    experience_level: Optional[str],
    max_jobs: Optional[int]
):
    """Background worker function executing the scraper pipeline."""
    tasks_db[task_id]["status"] = "running"
    try:
        result = run_scraper(
            job_title=job_title,
            location=location,
            remote=remote,
            date_posted=date_posted,
            experience_level=experience_level,
            max_jobs=max_jobs
        )
        tasks_db[task_id]["status"] = result.get("status", "completed")
        tasks_db[task_id]["result"] = result
    except Exception as e:
        tasks_db[task_id]["status"] = "failed"
        tasks_db[task_id]["error"] = str(e)


@app.get("/", tags=["General"])
def home():
    return {
        "message": "Welcome to the LinkedIn Job Scraper API!",
        "version": "2.1.0",
        "docs_url": "/docs",
        "headless_mode": settings.HEADLESS,
        "default_max_jobs": settings.MAX_JOBS,
        "supported_filters": {
            "date_posted": ["past_24h", "past_week", "past_month"],
            "experience_level": ["internship", "entry", "associate", "mid_senior", "director", "executive"]
        }
    }


@app.get("/health", tags=["General"])
def health_check():
    return {
        "status": "healthy",
        "headless": settings.HEADLESS,
        "sheet_configured": bool(settings.GOOGLE_CREDS_ENV or settings.GOOGLE_CREDS_FILE)
    }


@app.post("/scrape", tags=["Scraper"])
def scrape_sync(request: ScrapeRequest):
    """
    Synchronously triggers the scraping pipeline and waits for completion.
    Best for local testing or small batches.
    """
    result = run_scraper(
        job_title=request.job_title,
        location=request.location or "",
        remote=request.remote or "no",
        date_posted=request.date_posted,
        experience_level=request.experience_level,
        max_jobs=request.max_jobs
    )

    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=result.get("message", "Scraping pipeline failed.")
        )

    return result


@app.post("/scrape/async", response_model=AsyncTaskResponse, status_code=status.HTTP_202_ACCEPTED, tags=["Scraper"])
def scrape_async(request: ScrapeRequest, background_tasks: BackgroundTasks):
    """
    Triggers the scraping pipeline in the background and returns a task_id immediately.
    Recommended for cloud hosting (Render) to prevent HTTP timeouts.
    """
    task_id = str(uuid.uuid4())
    tasks_db[task_id] = {
        "task_id": task_id,
        "status": "queued",
        "request": request.model_dump(),
        "result": None,
        "error": None
    }

    background_tasks.add_task(
        background_scrape_worker,
        task_id=task_id,
        job_title=request.job_title,
        location=request.location or "",
        remote=request.remote or "no",
        date_posted=request.date_posted,
        experience_level=request.experience_level,
        max_jobs=request.max_jobs
    )

    return {
        "message": "Scrape task initiated in background.",
        "task_id": task_id,
        "status_check_url": f"/tasks/{task_id}"
    }


@app.get("/tasks/{task_id}", response_model=TaskStatusResponse, tags=["Tasks"])
def get_task_status(task_id: str):
    """
    Queries the status of an asynchronous scrape task.
    """
    task = tasks_db.get(task_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task ID '{task_id}' not found."
        )
    return task
