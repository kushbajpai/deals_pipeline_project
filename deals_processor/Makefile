# Makefile for deals_processor

.PHONY: help install dev test lint format type-check clean run

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies with pip"
	@echo "  make dev          - Install development dependencies"
	@echo "  make run          - Run development server (auto-reload)"
	@echo "  make run-prod     - Run production server"
	@echo "  make run-cli      - Run using CLI entry point"
	@echo "  make run-module   - Run as Python module"
	@echo "  make test         - Run tests"
	@echo "  make test-cov     - Run tests with coverage report"
	@echo "  make lint         - Run ruff linter"
	@echo "  make lint-fix     - Run ruff with auto-fix"
	@echo "  make format       - Format code with black"
	@echo "  make type-check   - Run mypy type checker"
	@echo "  make check-all    - Run all checks (lint, type, format)"
	@echo "  make clean        - Clean build artifacts and cache"

install:
	pip install -e .

dev:
	pip install -e ".[dev]"

run:
	uvicorn deals_processor.main:app --reload --host 0.0.0.0 --port 8000

run-prod:
	deals-processor

run-cli:
	deals-processor-dev

run-module:
	python -m deals_processor

test:
	pytest

test-cov:
	pytest --cov=src/deals_processor --cov-report=html

lint:
	ruff check src/ tests/

lint-fix:
	ruff check --fix src/ tests/

format:
	black src/ tests/

type-check:
	mypy src/

check-all: lint format type-check test
	@echo "All checks passed!"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name .coverage -exec rm {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf build/ dist/ *.egg-info 2>/dev/null || true
