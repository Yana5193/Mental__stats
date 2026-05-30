"""Эндпоинты выдачи вопросов и добавления новых тестов психологом."""

import json
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

app = FastAPI(title="questions_service", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

QUESTIONS_FILE = os.path.join(os.path.dirname(__file__), "questions.json")


def _load() -> dict:
    with open(QUESTIONS_FILE, encoding="utf-8") as f:
        return json.load(f)


def _save(data: dict):
    with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@app.get("/tests")
def list_tests():
    return _load()["tests"]


@app.get("/tests/{test_id}/questions")
def get_questions(test_id: int):
    tests = _load()["tests"]
    for t in tests:
        if t["id"] == test_id:
            return {
                "test_id": test_id,
                "name": t["name"],
                "questions": t["questions"],
                "consistency_pairs": t.get("consistency_pairs", []),
            }
    raise HTTPException(status_code=404, detail="Тест не найден")


class AddQuestionRequest(BaseModel):
    test_id: int
    question: str


class AddTestRequest(BaseModel):
    name: str


@app.post("/tests", status_code=201)
def add_test(body: AddTestRequest):
    data = _load()
    new_id = max((t["id"] for t in data["tests"]), default=0) + 1
    data["tests"].append({"id": new_id, "name": body.name, "questions": []})
    _save(data)
    return {"id": new_id, "name": body.name}


@app.post("/questions", status_code=201)
def add_question(body: AddQuestionRequest):
    data = _load()
    for t in data["tests"]:
        if t["id"] == body.test_id:
            t["questions"].append(body.question)
            _save(data)
            return {"added": body.question, "test_id": body.test_id}
    raise HTTPException(status_code=404, detail="Тест не найден")