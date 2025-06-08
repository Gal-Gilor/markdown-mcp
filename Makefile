# Makefile 

.PHONY: lint

lint:
	@echo "Running ruff checking linting and formatting..."
	poetry run ruff check .

.PHONY: test
test:
	poetry run pytest