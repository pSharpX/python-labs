-include .env
export

HF_HUB_DISABLE_PROGRESS_BARS=1

sync:
	uv sync --all-groups
install:
	uv pip install -r pyproject.toml

run:
	uv run main.py

# work
#guard_init:
#	python -m guardrails_ai.detect_pii.post_install

# work
#guard_init:
#	python -m guardrails_ai.toxic_language.post_install

# DID NOT work
#guard_init:
#	python -m guardrails_ai.detect_jailbreak.post_install

#guard_init:
#	python -m guardrails_ai.detect_system_prompt_leakage.post_install

guard_init:
	python -m guardrails_ai.valid_length.post_install

