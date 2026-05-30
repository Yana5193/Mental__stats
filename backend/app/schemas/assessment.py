"""Валидация отправляемых на бэк результатов тестов."""

from pydantic import BaseModel
from typing import List

class SubmitAnswersRequest(BaseModel):
    emp_id: int
    answers: List[int]
    consistency_pairs: List[List[int]] = []
    
    @field_validator("answers")
    @classmethod
    def answers_must_be_valid(cls, v: List[int]) -> List[int]:
        for i, a in enumerate(v):
            if not (1 <= a <= 5):
                raise ValueError(f"Ответ {i} должен быть от 1 до 5, получено {a}")
        return v

class AssesmentResult(BaseModel):
    emp_id: int
    total_points: int
    status: str
    advice: str
        

