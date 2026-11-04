import sys
import time
import threading
from pathlib import Path

# Add project root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import requests
import uvicorn
from app import app


def run_api_tests():
    port = 8088
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    # Wait for server to start
    base_url = f"http://127.0.0.1:{port}"
    for _ in range(10):
        try:
            r = requests.get(f"{base_url}/health", timeout=2)
            if r.status_code == 200:
                break
        except Exception:
            time.sleep(0.5)

    print("=" * 60)
    print(" FastAPI REST API Integration Test")
    print("=" * 60)

    # 1. Test GET /
    print("[*] Testing GET / ...")
    r = requests.get(f"{base_url}/")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    print("    Response:", r.json())

    # 2. Test GET /health
    print("\n[*] Testing GET /health ...")
    r = requests.get(f"{base_url}/health")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    print("    Response:", r.json())

    # 3. Test POST /scrape/async
    print("\n[*] Testing POST /scrape/async (non-blocking task trigger) ...")
    payload = {
        "job_title": "AI Engineer",
        "location": "India",
        "remote": "no",
        "max_jobs": 2
    }
    r = requests.post(f"{base_url}/scrape/async", json=payload)
    assert r.status_code == 202, f"Expected 202 Accepted, got {r.status_code}"
    data = r.json()
    task_id = data["task_id"]
    print("    Status: 202 Accepted")
    print(f"    Assigned Task ID: {task_id}")
    print(f"    Check URL: {data['status_check_url']}")

    # 4. Test GET /tasks/{task_id}
    print(f"\n[*] Polling GET /tasks/{task_id} ...")
    r = requests.get(f"{base_url}/tasks/{task_id}")
    assert r.status_code == 200, f"Expected 200, got {r.status_code}"
    task_info = r.json()
    print(f"    Current Task Status: '{task_info['status']}'")

    print("\n[OK] All REST API endpoints validated successfully!")
    print("=" * 60)

    # Shutdown server
    server.should_exit = True


if __name__ == "__main__":
    run_api_tests()
