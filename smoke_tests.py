"""Smoke-тесты: проверка доступности всех сервисов."""

import sys
import requests

BASE_APP = "http://localhost:8000"
BASE_QUESTIONS = "http://localhost:8001"
BASE_NOTIFICATION = "http://localhost:8002"
BASE_FRONTEND = "http://localhost:80"

PASSED = []
FAILED = []


def check(description, method, url, expected_status, **kwargs):
    try:
        r = requests.request(method, url, timeout=3, **kwargs)
        if r.status_code == expected_status:
            print(f"  PASS  {description}")
            PASSED.append(description)
        else:
            print(f"  FAIL  {description} — ожидался {expected_status}, получен {r.status_code}")
            FAILED.append(description)
    except requests.exceptions.ConnectionError:
        print(f"  FAIL  {description} — сервис недоступен ({url})")
        FAILED.append(description)
    except requests.exceptions.Timeout:
        print(f"  FAIL  {description} — таймаут ({url})")
        FAILED.append(description)


print("\n=== Smoke Tests ===\n")

check("GET /api/v1/analytics → 200",  "GET",  f"{BASE_APP}/api/v1/analytics", 200)
check("POST /api/v1/login без данных → 401", "POST", f"{BASE_APP}/api/v1/login",
      401, json={"full_name": "", "password": ""})
check("GET /tests → 200",             "GET",  f"{BASE_QUESTIONS}/tests", 200)
check("GET /health → 200",            "GET",  f"{BASE_NOTIFICATION}/health", 200)
check("GET / (frontend) → 200",       "GET",  f"{BASE_FRONTEND}/", 200)

print(f"\nРезультат: {len(PASSED)} passed, {len(FAILED)} failed")

if FAILED:
    sys.exit(1)
