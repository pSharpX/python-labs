-include .env
export


COMPOSE_PROFILES=workflow

build:
	docker compose up --build
initialize:
	docker compose up
start:
	docker compose start
down:
	docker compose down
destroy:
	docker compose down -v


sync:
	uv sync --all-groups
install:
	uv pip install -r pyproject.toml

test:
	deepeval test run evals.py
run:
	uv run main.py
serve:
	uvicorn src.api.main:app --reload --port 8000
scan:
	uv run security.py
