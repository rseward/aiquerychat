.PHONY: venv deps test lint run

venv:
	uv venv

deps:
	uv sync
	uv pip install --python .venv/bin/python -e .

test:
	uv run pytest

lint:
	uv run ruff check src/

run:
	uv run python -m aiquerychat
