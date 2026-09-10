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
scan:
	uv run security.py

guardrails_init:
	python -m guardrails_ai.guardrails_pii.post_install \
	guardrails_ai.detect_prompt_injection.post_install
