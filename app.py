"""
Root ASGI application entrypoint.
Delegates to the modular src.api package.
"""
from src.api.routes import app
from src.api.schemas import ScrapeRequest

__all__ = ["app", "ScrapeRequest"]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
