-include .env
export

CHANGELOG_DIR=$(PWD)/db/changelog
GENERATED_DIR=$(PWD)/db/changelog

DB_JDBC_URL=jdbc:postgresql://host.docker.internal:5432/vectordb
COMPOSE_PROFILES=rag

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

run:
	uv run main.py
