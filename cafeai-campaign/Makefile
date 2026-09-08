-include .env
export

sync:
	uv sync --all-groups
install:
	uv pip install -r pyproject.toml

test:
	deepeval test run evals.py
run:
	uv run main.py
