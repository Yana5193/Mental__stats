
RETEST_PERIOD_DAYS = 30

# (min_inclusive, max_inclusive, label, advice)
SCORE_THRESHOLDS = [
    (0,  15, "Норма",         "Всё в порядке."),
    (16, 30, "В зоне риска",  "Рекомендуем отдых."),
    (31, 999, "Нужна беседа", "Высокий уровень стресса!"),
]
