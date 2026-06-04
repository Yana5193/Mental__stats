.PHONY: help setup test test-lib coverage run compose-up compose-down smoke check build-lib install-lib-local docs clean

help:
	@echo "Доступные команды:"
	@echo "  make setup             - установить зависимости"
	@echo "  make test              - запустить все тесты"
	@echo "  make test-lib          - тесты только shared_lib"
	@echo "  make coverage          - отчёт о покрытии"
	@echo "  make run               - запустить через docker compose"
	@echo "  make compose-up        - собрать и запустить контейнеры"
	@echo "  make compose-down      - остановить контейнеры"
	@echo "  make smoke             - smoke-тесты (сервисы должны быть запущены)"
	@echo "  make check             - test + build-lib (полная проверка)"
	@echo "  make build-lib         - собрать пакет psych-analyzer"
	@echo "  make install-lib-local - установить пакет локально"
	@echo "  make docs              - показать где лежит документация"
	@echo "  make clean             - удалить временные файлы"

setup:
	pip install -e shared_lib/
	pip install -r backend/requirements.txt

test:
	cd backend && python -m pytest tests/test_api.py -v
	cd backend/questions_service && python -m pytest test/ -v
	cd backend/notification_service && python -m pytest test/ -v
	python -m pytest shared_lib/tests/ -v

coverage:
	python -m pytest \
		backend/tests/test_api.py \
		backend/questions_service/test/ \
		backend/notification_service/test/ \
		shared_lib/tests/ \
		--cov=backend/app \
		--cov=backend/questions_service \
		--cov=backend/notification_service \
		--cov=shared_lib/src/psych_analyzer \
		--cov-report=term-missing \
		--cov-report=html:htmlcov

test-lib:
	python -m pytest shared_lib/tests/ -v

run: compose-up

compose-up:
	docker compose up --build -d

compose-down:
	docker compose down -v

check: test build-lib
	@echo "Проверка пройдена успешно"

build-lib:
	pip install build
	python -m build shared_lib/ --outdir dist/

install-lib-local:
	pip install -e shared_lib/

docs:
	@echo "Документация находится в docs/"
	@echo "  docs/specification.md  - требования"
	@echo "  docs/architecture.md   - архитектура"
	@echo "  backend/app/domain.md  - предметная область"
	@echo "  docs/diagrams/         - диаграммы"

smoke:
	python smoke_tests.py

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.db" -delete 2>/dev/null || true
	rm -rf htmlcov .coverage 2>/dev/null || true
