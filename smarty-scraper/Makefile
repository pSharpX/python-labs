-include .env
export

test:
	pytest

sync:
	uv sync --all-groups
install:
	uv pip install -r pyproject.toml

initialize:
	docker compose up
start:
	docker compose start
down:
	docker compose down
destroy:
	docker compose down -v

run:
	uv run  main.py