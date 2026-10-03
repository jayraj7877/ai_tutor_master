.PHONY: help install dev test docker-up docker-down migrate

help:
	@echo "AI English Tutor Backend Makefile"
	@echo "  install    Install dependencies in virtual environment"
	@echo "  dev        Run FastAPI dev server"
	@echo "  test       Run unit and integration tests"
	@echo "  docker-up  Start Docker Compose services"
	@echo "  docker-down Stop Docker Compose services"
	@echo "  migrate    Run Alembic database migrations"

install:
	pip install --upgrade pip
	pip install -r requirements.txt

dev:
	uvicorn app.main:app --reload --port 8000

test:
	pytest -v

docker-up:
	docker compose up -d --build

docker-down:
	docker compose down

migrate:
	alembic upgrade head
