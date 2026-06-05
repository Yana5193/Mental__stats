# Mental Stats

Веб-система мониторинга психологического состояния сотрудников организации. Позволяет выявить уровень стресса и эмоционального выгорания через периодическое тестирование.

## Быстрый старт

```bash
git clone https://github.com/Yana5193/Mental__stats.git
cd Mental__stats
make setup
make test
make compose-up
```

Приложение доступно на `http://localhost` (frontend, порт 80).

## Структура репозитория

| Папка | Назначение |
|---|---|
| `shared_lib/` | Переиспользуемая библиотека `psych_analyzer` (TestPyPI) |
| `backend/app/` | Основной FastAPI-сервис (порт 8000) |
| `backend/questions_service/` | Сервис вопросов (порт 8001) |
| `backend/notification_service/` | Сервис уведомлений (порт 8002) |
| `frontend/` | Web UI на nginx (порт 80) |
| `docs/` | Документация проекта |

## Основные команды

| Команда | Описание |
|---|---|
| `make setup` | Установить зависимости |
| `make test` | Запустить все тесты |
| `make coverage` | Отчёт о покрытии |
| `make compose-up` | Запустить через Docker Compose |
| `make docs` | Собрать документацию |
| `make build-lib` | Собрать пакет psych_analyzer |
