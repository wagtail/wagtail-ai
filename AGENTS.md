# Agents

Important context for AI coding agents working on this project.

## Project structure

Wagtail AI is a Django/Wagtail package providing AI-powered content assistance.

- `src/wagtail_ai/` - the package source code
- `src/wagtail_ai/static_src/` - React/TypeScript frontend source
- `tests/` - test suite with Django test app in `tests/testapp/`
- `docs/` - mkdocs documentation

## Key commands

```sh
just help              # View all commands
just install           # Install Python and Node.js dependencies (uv sync --dev && npm ci)
just demo              # Run the test app (migrate + runserver)
just test              # Run tests with pytest
just test-lowest-deps  # Run tests with lowest supported Python and dependency versions
just test-highest-deps # Run tests with highest supported dependency versions
just coverage          # Run tests with coverage report
just lint              # Run all linters (Ruff, pre-commit, Prettier, Stylelint)
just format            # Run all formatters (Ruff, Prettier)
just build             # Build static files and package for distribution
```

## Linting and type checking

```sh
just lint              # Ruff format check, Ruff lint, pre-commit hooks, Prettier/Stylelint
uv run pre-commit run --all-files  # Run pre-commit hooks directly
npx pyright            # Type check (configured in pyproject.toml [tool.pyright])
```

## Build system

- Build backend: `uv_build` (configured in `pyproject.toml`)
- Frontend build: Webpack (configured in `webpack.config.js`)
- Package build: `uv build` (produces wheel + sdist in `dist/`)
- Static files: built to `src/wagtail_ai/static/wagtail_ai/`

## Testing matrix

Tests run across Python 3.11-3.14, Django 5.2/6.0, and Wagtail 7.4+.
Tox handles the full matrix locally; CI runs both tox-based tests and
lowest/highest dependency checks via uv.
