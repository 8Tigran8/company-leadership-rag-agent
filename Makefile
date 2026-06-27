.PHONY: install test lint format smoke

install:
	uv sync

test:
	uv run pytest

lint:
	uv run ruff check .

format:
	uv run ruff format .

smoke:
	uv run company-rag --help

