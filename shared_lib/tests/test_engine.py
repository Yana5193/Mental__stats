import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from psych_analyzer.engine import calculate_score, get_status


class TestCalculateScore:
    def test_sums_valid_answers(self):
        assert calculate_score([1, 2, 3, 4, 5]) == 15

    def test_low_answers_valid(self):
        # 7 из 10 одинаковых — ниже порога 80%, валидно
        assert calculate_score([1, 1, 1, 1, 1, 1, 1, 2, 3, 4]) == 16

    def test_high_answers_valid(self):
        # 7 из 10 одинаковых — ниже порога 80%, валидно
        assert calculate_score([5, 5, 5, 5, 5, 5, 5, 4, 3, 2]) == 44

    def test_all_same_raises_monotone(self):
        with pytest.raises(ValueError, match="одинаковы"):
            calculate_score([1] * 10)

    def test_single_answer(self):
        assert calculate_score([3]) == 3

    def test_empty_answers_gives_zero(self):
        assert calculate_score([]) == 0

    def test_raises_on_zero(self):
        with pytest.raises(ValueError, match="от 1 до 5"):
            calculate_score([0])

    def test_raises_on_six(self):
        with pytest.raises(ValueError, match="от 1 до 5"):
            calculate_score([6])

    def test_raises_on_negative(self):
        with pytest.raises(ValueError):
            calculate_score([-1])

    def test_raises_on_float(self):
        with pytest.raises(ValueError):
            calculate_score([1.5])

    def test_raises_on_string(self):
        with pytest.raises(ValueError):
            calculate_score(["3"])


class TestGetStatus:
    def test_norm_lower_bound(self):
        result = get_status(0)
        assert result["label"] == "Норма"

    def test_norm_upper_bound(self):
        result = get_status(15)
        assert result["label"] == "Норма"

    def test_risk_lower_bound(self):
        result = get_status(16)
        assert result["label"] == "В зоне риска"

    def test_risk_upper_bound(self):
        result = get_status(30)
        assert result["label"] == "В зоне риска"

    def test_critical_lower_bound(self):
        result = get_status(31)
        assert result["label"] == "Нужна беседа"

    def test_critical_high_score(self):
        result = get_status(50)
        assert result["label"] == "Нужна беседа"

    def test_advice_is_present(self):
        result = get_status(10)
        assert "advice" in result
        assert len(result["advice"]) > 0

    def test_raises_on_negative_score(self):
        with pytest.raises(ValueError, match="отрицательным"):
            get_status(-1)