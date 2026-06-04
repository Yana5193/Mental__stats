"""Тесты backend API: login, submit, analytics, departments."""


def test_login_valid_credentials(client):
    r = client.post("/api/v1/login", json={
        "full_name": "Тестов Тест Тестович", "password": "test123"
    })
    assert r.status_code == 200
    data = r.json()
    assert "emp_id" in data
    assert data["full_name"] == "Тестов Тест Тестович"


def test_login_wrong_password(client):
    r = client.post("/api/v1/login", json={
        "full_name": "Тестов Тест Тестович", "password": "wrong"
    })
    assert r.status_code == 401


def test_submit_valid_answers(client):
    emp_id = client.post("/api/v1/login", json={
        "full_name": "Тестов Тест Тестович", "password": "test123"
    }).json()["emp_id"]

    r = client.post("/api/v1/submit", json={
        "emp_id": emp_id,
        "answers": [1, 2, 3, 2, 1, 2, 3, 2, 1, 2]
    })
    assert r.status_code == 200
    assert r.json()["total_points"] == 19


def test_submit_retest_blocked(client):
    emp_id = client.post("/api/v1/login", json={
        "full_name": "Тестов Тест Тестович", "password": "test123"
    }).json()["emp_id"]
    payload = {"emp_id": emp_id, "answers": [1, 2, 3, 2, 1, 2, 3, 2, 1, 2]}

    client.post("/api/v1/submit", json=payload)
    r = client.post("/api/v1/submit", json=payload)
    assert r.status_code == 429


def test_submit_monotone_answers(client):
    emp_id = client.post("/api/v1/login", json={
        "full_name": "Тестов Тест Тестович", "password": "test123"
    }).json()["emp_id"]

    r = client.post("/api/v1/submit", json={
        "emp_id": emp_id,
        "answers": [3, 3, 3, 3, 3, 3, 3, 3, 3, 3]
    })
    assert r.status_code == 422


def test_submit_inconsistent_answers(client):
    emp_id = client.post("/api/v1/login", json={
        "full_name": "Тестов Тест Тестович", "password": "test123"
    }).json()["emp_id"]

    r = client.post("/api/v1/submit", json={
        "emp_id": emp_id,
        "answers": [1, 1, 3, 3, 3, 3, 3, 3, 3, 5],
        "consistency_pairs": [[0, 9], [1, 9]]
    })
    assert r.status_code == 422


def test_analytics_returns_list(client):
    r = client.get("/api/v1/analytics")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


def test_departments_returns_list(client):
    r = client.get("/api/v1/departments")
    assert r.status_code == 200
    assert isinstance(r.json(), list)