.DEFAULT_GOAL := help
SHELL := /bin/bash


.PHONY: install ## install required dependencies on bare metal
install:
	uv sync --refresh


.PHONY: format ## Run the formatter on bare metal
format:
	uv run tox -e format


.PHONY: lint ## run the linter on bare metal
lint:
	uv run tox -e lint


.PHONY: test ## run unit tests on bare metal
test:
	uv run tox -e test


.PHONY: publish ## Build & publish the package to Nexus. Ensure to have UV_PUBLISH_USERNAME & UV_PUBLISH_PASSWORD environment variables set.
publish:
	@version=$$(grep '^version *= *' pyproject.toml | head -1 | sed 's/version *= *"\(.*\)"/\1/'); \
	echo "Current version: $$version"; \
	read -p "Publish version $$version? (y/n): " confirm; \
	if [ "$$confirm" = "y" ]; then \
		uv build --no-sources && \
		uv publish --verbose; \
	else \
		echo "Publish cancelled."; \
	fi