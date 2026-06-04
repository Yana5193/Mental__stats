"""Тесты микросервиса уведомлений."""

import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_health_returns_ok():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_alert_accepted_for_critical_score(capsys):
    r = client.post("/alert", json={"emp_id": 1, "score": 42})
    assert r.status_code == 202
    assert r.json()["status"] == "logged"


def test_alert_logs_emp_id(capsys):
    client.post("/alert", json={"emp_id": 7, "score": 35})
    captured = capsys.readouterr()
    assert "7" in captured.out


def test_alert_missing_score_rejected():
    r = client.post("/alert", json={"emp_id": 1})
    assert r.status_code == 422


def test_alert_missing_emp_id_rejected():
    r = client.post("/alert", json={"score": 40})
    assert r.status_code == 422


def test_alert_negative_score_accepted():
    r = client.post("/alert", json={"emp_id": 1, "score": -1})
    assert r.status_code == 202

def test_alert_empty_body_rejected():
    r = client.post("/alert", json={})
    assert r.status_code == 422