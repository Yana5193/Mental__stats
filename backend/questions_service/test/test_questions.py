import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_list_tests_returns_array():
    r = client.get("/tests")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
    assert len(r.json()) > 0


def test_get_questions_for_existing_test():
    r = client.get("/tests/1/questions")
    assert r.status_code == 200
    data = r.json()
    assert "questions" in data
    assert len(data["questions"]) > 0


def test_get_questions_for_unknown_test():
    r = client.get("/tests/9999/questions")
    assert r.status_code == 404


def test_add_question_to_existing_test(tmp_path, monkeypatch):
    import shutil, os, json
    src = os.path.join(os.path.dirname(__file__), "..","questions.json")
    tmp_file = tmp_path / "questions.json"
    shutil.copy(src, tmp_file)

    import main as m
    monkeypatch.setattr(m, "QUESTIONS_FILE", str(tmp_file))

    r = client.post("/questions", json={"test_id": 1, "question": "Тестовый вопрос"})
    assert r.status_code == 201
    assert r.json()["added"] == "Тестовый вопрос"


def test_add_question_to_unknown_test():
    r = client.post("/questions", json={"test_id": 9999, "question": "X"})
    assert r.status_code == 404
    
def test_get_questions_for_existing_test():
    r = client.get("/tests/1/questions")
    assert r.status_code == 200
    data = r.json()
    assert "questions" in data
    assert len(data["questions"]) > 0
    assert "consistency_pairs" in data     

def test_add_test(tmp_path, monkeypatch):
    import shutil, os
    src = os.path.join(os.path.dirname(__file__), "..", "questions.json")
    tmp_file = tmp_path / "questions.json"
    shutil.copy(src, tmp_file)

    import main as m
    monkeypatch.setattr(m, "QUESTIONS_FILE", str(tmp_file))

    r = client.post("/tests", json={"name": "Новый тест"})
    assert r.status_code == 201

