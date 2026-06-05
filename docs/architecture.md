# Архитектура: mental_stats

## Компоненты

```
┌─────────────────────────────────────────────────────┐
│                     Browser                         │
│  login.html  assigment.html  index.html             │
└──────────────────────┬──────────────────────────────┘
                       │ HTTP (fetch)
          ┌────────────▼────────────┐
          │   frontend (nginx :80)  │
          └────────────┬────────────┘
                       │
          ┌────────────▼────────────┐
          │    app (FastAPI :8000)  │  ← главный бэкенд
          │  /api/v1/login          │
          │  /api/v1/submit         │
          │  /api/v1/analytics      │
          └──┬──────────────────┬───┘
             │                  │
  ┌──────────▼──────┐   ┌───────▼────────────────┐
  │ questions_service│   │ notification_service    │
  │  FastAPI :8001   │   │   FastAPI :8002          │
  │  /tests          │   │   /alert  /health        │
  └──────────────────┘   └────────────────────────┘

  ┌─────────────────────────┐   ┌──────────────────────┐
  │      shared_lib          │   │   SQLite (volume)     │
  │  psych_analyzer          │   │   employees           │
  │  engine.py  constants.py │   │   staff_status        │
  └──────────────────────────┘   └──────────────────────┘
           ↑                              ↑
           └── используется app ──────────┘
```

## Контекстная диаграмма

```mermaid
flowchart TD
    Employee["Сотрудник"]
    Psychologist[" Психолог"]
    Manager["Менеджер"]

    Frontend["frontend\nnginx :80"]
    App["app\nFastAPI :8000"]
    QS["questions_service\nFastAPI :8001"]
    NS["notification_service\nFastAPI :8002"]
    Lib["shared_lib\npsych_analyzer"]
    DB[("SQLite\nmental_health.db")]

    Employee -->|"вход + тест"| Frontend
    Psychologist -->|"аналитика"| Frontend
    Manager -->|"аналитика"| Frontend

    Frontend -->|"REST"| App
    Frontend -->|"GET /questions"| QS

    App -->|"calculate_score()\nget_status()"| Lib
    App -->|"read/write"| DB
    App -->|"POST /alert"| NS
```

## Граница переиспользуемой логики

`shared_lib/src/psych_analyzer` — чистая библиотека без зависимостей от FastAPI или БД.
Опубликована на TestPyPI как пакет `psych_analyzer` и устанавливается в Docker-образ командой:

```
pip install --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple/ \
            psych-analyzer
```

Для локальной разработки и тестов: `pip install -e shared_lib/`

## Поток данных: прохождение теста

1. Браузер → `login.html` → POST `/api/v1/login` → получает `emp_id`
2. Браузер → `assigment.html` → GET `questions_service:8001/tests/1/questions`
3. Сотрудник отвечает → POST `/api/v1/submit` с `emp_id`, массивом ответов и `consistency_pairs`
4. `app` вызывает `psych_analyzer.calculate_score()` и `get_status()`
5. Результат сохраняется в SQLite
6. Если статус "Нужна беседа" → POST `notification_service:8002/alert`

## Диаграмма последовательности: прохождение теста

```mermaid
sequenceDiagram
    actor E as Сотрудник
    participant F as frontend
    participant A as app :8000
    participant Q as questions_service :8001
    participant L as psych_analyzer
    participant N as notification_service :8002
    participant DB as SQLite

    E->>F: открывает login.html
    E->>F: вводит ФИО + пароль
    F->>A: POST /api/v1/login
    A->>DB: SELECT employee WHERE name=...
    DB-->>A: emp_id
    A-->>F: {emp_id, full_name}

    F->>Q: GET /tests/1/questions
    Q-->>F: список вопросов

    loop Каждый вопрос
        F-->>E: показывает вопрос
        E->>F: выбирает ответ 1–5
    end

    F->>A: POST /api/v1/submit {emp_id, answers, consistency_pairs}
    A->>L: calculate_score(answers, consistency_pairs)
    L-->>A: total_points
    A->>L: get_status(total_points)
    L-->>A: {label, advice}
    A->>DB: INSERT staff_status
    alt статус = "Нужна беседа"
        A->>N: POST /alert
        N-->>A: 202 logged
    end
    A-->>F: {total_points, status, advice}
    F-->>E: показывает результат
```

## Сервисы и порты

| Сервис | Порт | Технология |
|---|---|---|
| frontend | 80 | nginx + HTML/CSS/JS |
| app | 8000 | FastAPI + SQLAlchemy |
| questions_service | 8001 | FastAPI + JSON |
| notification_service | 8002 | FastAPI |
