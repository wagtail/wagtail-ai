# Task runner: https://github.com/casey/just
# Requires: `uv`, `npm`, and `just`.

# List all the justfile recipes.
help:
    just --list --list-prefix 'just '

# Remove all the Python and Node.js cache files.
clean-pyc:
    find . -name '*.pyc' -exec rm -f {} +
    find . -name '*.pyo' -exec rm -f {} +
    find . -name '*~' -exec rm -f {} +

# Install the dependencies.
install: clean-pyc
    uv sync --dev
    npm ci

# Lint the server code.
lint-server:
    uv run ruff format --check .
    uv run ruff check .
    SKIP=ruff-check,ruff-format,lint:css,lint:format uv run prek run --all-files

# Lint the client code.
lint-client:
    npm run lint --loglevel silent

# Run all linters.
lint: lint-server lint-client

# Format the server code.
format-server:
    uv run ruff check . --fix
    uv run ruff format .
    SKIP=ruff-check,ruff-format,lint:css,lint:format uv run prek run --all-files

# Format the client code.
format-client:
    npm run format

# Run all formatters.
format: format-server format-client

# Run tests with pytest.
test:
    uv run pytest

# Run tests with lowest supported Python and direct dependency versions.
test-lowest-deps:
    #!/usr/bin/env bash
    set -euo pipefail
    lowest_python=$(uv run python -c 'import tomllib; print(tomllib.load(open("pyproject.toml","rb"))["project"]["requires-python"].removeprefix(">=").strip())')
    uv run --isolated --python "$lowest_python" --resolution lowest-direct pytest

# Run tests with highest supported dependency versions.
test-highest-deps:
    uv run --isolated --with 'Django, Wagtail' pytest

# Run tests with coverage.
coverage:
    uv run coverage run -m pytest
    uv run coverage report -m
    uv run coverage html

# Build static files.
build-static:
    npm run build

# Build the package for distribution.
build: build-static
    uv build
