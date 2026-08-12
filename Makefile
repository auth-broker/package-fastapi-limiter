.DEFAULT_GOAL := help
SHELL := /bin/bash

.PHONY: help ## Show this help message
help:
	@grep -E '^\.PHONY: [a-zA-Z_-]+ .*?## .*$$' $(MAKEFILE_LIST) | sed 's/\.PHONY: \(.*\) ## \(.*\)/\1 - \2/'

.PHONY: install ## Install dependencies on bare metal
install:
	uv sync --refresh

.PHONY: format ## Run the formatter on bare metal
format:
	uv run ruff format
	uv run ruff check --fix

.PHONY: lint ## run the linter on bare metal
lint:
	uv run ruff check
	uv run ruff format --check

.PHONY: build ## Build the package
build:
	uv build

.PHONY: test ## run unit tests on bare metal
test:
	uv run pytest -v -m "not integration"

.PHONY: ci ## Run CI checks locally
ci: lint test
