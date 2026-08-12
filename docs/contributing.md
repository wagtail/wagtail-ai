# Contributing to Wagtail AI

## Getting the Code

To make changes to this project, first clone this repository:

```shell
git clone https://github.com/wagtail/wagtail-ai.git
cd wagtail-ai
```

## Setting up your development environment

We use [just](https://github.com/casey/just) as a task runner, [uv](https://docs.astral.sh/uv/) to manage Python dependencies, and npm for Node.js dependencies. Make sure you have both installed.

Then you can install the dependencies:

```shell
just install
```

This runs `uv sync --dev` and `npm ci` under the hood.

### Using devcontainers

A [devcontainer](https://containers.dev/) configuration is available in this repository, with uv and Node.js pre-installed.

## Working with the test application

A Wagtail example for testing/development is bundled in this repo (find it at `tests/testapp`).

You can interact with this application using the `testmanage.py` script as you would a normal Django/Wagtail app. For example, to bring up a development server:

```shell
uv run testmanage.py migrate
uv run testmanage.py runserver 0:8000
```

## Building frontend assets

Frontend assets (React components, admin scripts, custom CSS) are bundled using Webpack. A Node.js environment is required to install and run the dependencies required to build these assets.

Assets can be built with:

```shell
npm run build
```

or in 'watch' mode with:

```shell
npm run start
```

## pre-commit

This project uses [pre-commit](https://github.com/pre-commit/pre-commit) to help keep to coding standards by automatically checking your commits.

```shell
# initialize pre-commit
uv run pre-commit install

# Optional, run all checks once for this, then the checks will run only on the changed files
uv run pre-commit run --all-files
```

## Running tests

You can run tests with:

```shell
just test
```

To run tests with coverage:

```shell
just coverage
```

To test with the lowest supported dependency versions:

```shell
just test-lowest-deps
```

To test with the highest supported dependency versions:

```shell
just test-highest-deps
```

For the full test matrix across Python, Django, and Wagtail versions, use tox:

```shell
tox
```

or for a specific environment: `tox -e python3.11-django5.2-wagtail7.4-sqlite`

## Linting and formatting

```shell
just lint    # Run all linters (Ruff, pre-commit, Prettier, Stylelint)
just format  # Run all formatters (Ruff, Prettier)
```

## Building the package

To build the package for distribution:

```shell
just build
```

This builds the frontend assets with Webpack, then builds the Python wheel and sdist with `uv build`.

## Building the documentation

Documentation for this package is built using `mkdocs`. These are automatically built by ReadTheDocs when pushed to GitHub, but you can build them locally:

```shell
uv sync --extra docs
uv run mkdocs build
```
