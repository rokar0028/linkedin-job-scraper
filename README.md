# LinkedIn Job Scraper & Google Sheets Synchronizer

An automated, resilient scraping pipeline built with **Playwright**, **FastAPI**, and **Google Sheets API**. Searches LinkedIn jobs based on title, location, and remote filters, automatically scrolls through results, extracts structured job information, and syncs newly discovered jobs into Google Sheets with deduplication.

---

## Project Structure

```text
linkdin_job_scraper/
├── src/                          # Core source package
│   ├── api/                      # REST API (FastAPI)
│   │   ├── routes.py             # Route handlers & background task workers
│   │   └── schemas.py            # Pydantic request & response models
│   ├── browser/                  # Browser automation layer
│   │   └── driver.py             # Playwright Chromium lifecycle & filter handling
│   ├── core/                     # Core system configuration
│   │   └── config.py             # Centralized settings & environment loading
│   ├── scraper/                  # Scraping & extraction engine
│   │   └── engine.py             # Dynamic scrolling & multi-strategy card parsing
│   ├── storage/                  # Data persistence layer
│   │   └── sheets.py             # Google Sheets API client & batch deduplication
│   └── pipeline.py               # End-to-end scraper orchestration
│
├── scripts/                      # Utility & operational scripts
│   ├── login.py                  # Interactive LinkedIn login session generator
│   └── test_sheets.py            # Isolated Google Sheets connectivity test
│
├── tests/                        # Automated unit tests
│   ├── test_config.py            # Configuration validation tests
│   └── test_schemas.py           # API schema validation tests
│
├── app.py                        # Root ASGI entrypoint (uvicorn app:app)
├── main.py                       # Root CLI entrypoint (python main.py)
├── login.py                      # Root shortcut for session generator
├── build.sh                      # Render/Linux deployment build script
├── requirements.txt              # Project dependencies (UTF-8 clean)
├── runtime.txt                   # Target Python runtime (python-3.12.10)
├── .env.example                  # Environment configuration template
└── README.md                     # Documentation
```

---

## Key Features

- **Automated Filtering**: Search by job title, targeted location, and optional Remote filter.
- **Dynamic Scrolling & Extraction**: Uses progressive container scrolling to trigger LinkedIn's lazy-loading mechanism up to your desired job limit.
- **Multi-Strategy Fallback Extraction**: Resilient to LinkedIn DOM changes and badges (verified, promoted, recruiter tags) to prevent blank or shifted fields.
- **Optimized Google Sheets Sync**:
  - Automatically initializes sheet headers if empty.
  - Queries only the job URL column for efficient deduplication.
  - Appends new jobs in a single batched API call to prevent rate limiting.
- **Dual Interfaces**:
  - **CLI (`main.py`)**: Fast, interactive terminal interface.
  - **REST API (`app.py`)**: Production-ready FastAPI app with both synchronous (`/scrape`) and non-blocking asynchronous (`/scrape/async`) endpoints with task polling.
- **Cloud-Ready**: Prepared for deployment on **Render**, **Railway**, or Docker with environment variable fallback and automated browser installation via `build.sh`.

---

## Quickstart & Local Setup

### 1. Prerequisites
- Python 3.10+
- Google Cloud Service Account credentials (`credentials.json`)
- A LinkedIn account

### 2. Installation
```bash
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
playwright install chromium
```

### 3. Generate LinkedIn Session (`auth.json`)
```bash
python login.py
# or: python scripts/login.py
```
A Chromium browser window will open. Complete your LinkedIn login (including 2FA/CAPTCHA if prompted). Once you see your LinkedIn feed, press Enter in the terminal. Your session will be saved as `auth.json` (git-ignored).

### 4. Verify Google Sheets Connection
```bash
python scripts/test_sheets.py
```

### 5. Run the Application

#### Option A: Interactive CLI
```bash
python main.py
```

#### Option B: FastAPI Web Server
```bash
uvicorn app:app --reload --port 8000
```
API Documentation: `http://localhost:8000/docs`.

---

## Running Unit Tests

Run the test suite with Python's built-in `unittest`:
```bash
python -m unittest discover tests
```

---

## Deploying to Render

1. **Build Command**:
   ```bash
   chmod +x build.sh && ./build.sh
   ```
2. **Start Command**:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port $PORT
   ```
3. **Environment Variables**:
   In your Render Dashboard, add:
   - `HEADLESS`: `true`
   - `LINKEDIN_AUTH`: Content of `auth.json`
   - `GOOGLE_CREDENTIALS`: Content of `credentials.json`
   - `GOOGLE_SHEET_NAME`: `LinkedIn Job Scraper`
