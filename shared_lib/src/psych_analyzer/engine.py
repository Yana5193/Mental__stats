"""Математический движок подсчёта индексов стресса."""

from typing import Iterable
from .constants import SCORE_THRESHOLDS

# Если доля одинаковых ответов превышает порог — тест считается нечестным
_MONOTONE_THRESHOLD = 0.8


def check_answer_pattern(answers: list[int]) -> None:
    """Raises ValueError если ответы выглядят как случайный клик (все одинаковые)."""
    if len(answers) < 2:
        return
    most_common_count = max(answers.count(v) for v in set(answers))
    if most_common_count / len(answers) >= _MONOTONE_THRESHOLD:
        raise ValueError(
            "Ответы выглядят неправдоподобно: слишком много одинаковых значений. "
            "Пожалуйста, отвечайте честно — это важно для вашего здоровья."
        )


def check_consistency(answers: list[int], pairs: list[list[int]], max_diff: int = 2) -> None:
    """Raises ValueError если похожие вопросы получили противоречивые ответы.

    pairs — список пар индексов вопросов которые должны быть близки по смыслу.
    max_diff — максимально допустимая разница между ответами в паре.
    Если нарушений >= 2 — тест считается невалидным.
    """
    if not pairs:
        return
    violations = [
        (i, j) for i, j in pairs
        if i < len(answers) and j < len(answers)
        and abs(answers[i] - answers[j]) > max_diff
    ]
    if len(violations) >= 2:
        raise ValueError(
            "Ответы выглядят противоречиво: на похожие вопросы даны очень разные ответы. "
            "Пожалуйста, отвечайте внимательно — это важно для вашего здоровья."
        )


def calculate_score(answers: Iterable[int],
                    consistency_pairs: list[list[int]] | None = None) -> int:
    """Суммирует ответы (каждый 1–5). Raises ValueError при нарушении диапазона,
    монотонном паттерне или противоречивых ответах."""
    answers = list(answers)
    total = 0
    for i, value in enumerate(answers):
        if not isinstance(value, int) or not (1 <= value <= 5):
            raise ValueError(f"Ответ {i} должен быть целым числом от 1 до 5, получено: {value!r}")
        total += value
    check_answer_pattern(answers)
    if consistency_pairs:
        check_consistency(answers, consistency_pairs)
    return total


def get_status(score: int) -> dict:
    """Возвращает {'label': str, 'advice': str} по набранным баллам."""
    for min_score, max_score, label, advice in SCORE_THRESHOLDS:
        if min_score <= score <= max_score:
            return {"label": label, "advice": advice}
    # score выше всех порогов → последний порог
    *_, last = SCORE_THRESHOLDS
    return {"label": last[2], "advice": last[3]}