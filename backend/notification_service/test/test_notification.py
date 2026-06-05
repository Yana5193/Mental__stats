"""Тесты микросервиса уведомлений."""

import os
import tempfile

import pytest


@pytest.fixture
def client(monkeypatch):
    tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
    tmp.close()
    monkeypatch.setenv("NOTIFICATION_DB_URL", f"sqlite:///{tmp.name}")

    import importlib
    import main
    importlib.reload(main)

    from fastapi.testclient import TestClient
    yield TestClient(main.app)

    main.engine.dispose()
    try:
        os.unlink(tmp.name)
    except PermissionError:
        pass


def test_health_returns_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_alert_accepted_for_critical_score(client):
    r = client.post("/alert", json={"emp_id": 1, "score": 42})
    assert r.status_code == 202
    assert r.json()["status"] == "logged"
    assert "alert_id" in r.json()


def test_alert_is_persisted(client):
    client.post("/alert", json={"emp_id": 7, "score": 35})
    r = client.get("/alerts")
    assert r.status_code == 200
    alerts = r.json()
    assert len(alerts) == 1
    assert alerts[0]["emp_id"] == 7
    assert alerts[0]["score"] == 35
    assert alerts[0]["is_read"] is False


def test_alerts_returned_newest_first(client):
    client.post("/alert", json={"emp_id": 1, "score": 31})
    client.post("/alert", json={"emp_id": 2, "score": 40})
    alerts = client.get("/alerts").json()
    assert alerts[0]["emp_id"] == 2
    assert alerts[1]["emp_id"] == 1


def test_unread_only_filter(client):
    r1 = client.post("/alert", json={"emp_id": 1, "score": 31}).json()
    client.post("/alert", json={"emp_id": 2, "score": 40})
    client.post(f"/alerts/{r1['alert_id']}/read")

    unread = client.get("/alerts?unread_only=true").json()
    assert len(unread) == 1
    assert unread[0]["emp_id"] == 2


def test_mark_read(client):
    alert_id = client.post("/alert", json={"emp_id": 1, "score": 33}).json()["alert_id"]
    r = client.post(f"/alerts/{alert_id}/read")
    assert r.status_code == 200
    assert r.json()["is_read"] is True

    alerts = client.get("/alerts").json()
    assert alerts[0]["is_read"] is True


def test_mark_read_nonexistent_returns_404(client):
    r = client.post("/alerts/999/read")
    assert r.status_code == 404


def test_alert_missing_score_rejected(client):
    r = client.post("/alert", json={"emp_id": 1})
    assert r.status_code == 422


def test_alert_missing_emp_id_rejected(client):
    r = client.post("/alert", json={"score": 40})
    assert r.status_code == 422


def test_alert_empty_body_rejected(client):
    r = client.post("/alert", json={})
    assert r.status_code == 422
