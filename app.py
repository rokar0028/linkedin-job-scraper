from fastapi import FastAPI
from pydantic import BaseModel

from main import run_scraper

app = FastAPI()


class ScrapeRequest(BaseModel):
    job_title: str
    location: str


@app.get("/")
def home():
    return {
        "message": "Welcome to the LinkedIn Job Scraper API!"
    }


@app.post("/scrape")
def scrape(request: ScrapeRequest):
    result = run_scraper(
        request.job_title,
        request.location
    )

    return result