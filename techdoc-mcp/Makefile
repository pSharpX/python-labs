-include .env
export


COMPOSE_PROFILES=rag

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

run:
	uv run main.py

mcp:
	uv run server.py

server:
	fastmcp run server.py:mcp --transport http --port 8000