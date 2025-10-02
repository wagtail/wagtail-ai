# Contributing to Wagtail AI

## Getting the Code

To make changes to this project, first clone this repository:

```shell
git clone https://github.com/wagtail-ai/wagtail-ai.git
cd wagtail-ai
```

## Setting up your development environment

The easiest way to bootstrap your development environment is using `tox`. We recommending installing this in an isolated environment using `pipx`:

```shell
python -m pip install pipx-in-pipx --user
pipx install tox
```

Alternative installation methods can be found in the [tox documentation](https://tox.wiki/en/latest/installation.html).

Once installed, create a development virtual environment with:

```shell
tox devenv -e interactive
. ./venv/bin/activate
```

### Using devcontainers

Alernatively, a [devcontainer](https://containers.dev/) configuration is available in this repository with `tox` configured.

Using this devcontainer in VSCode will automatically enable the virtual environment, in other devcontainer environments you will need to activate it with `. ./venv/bin/activate`.

## Working with the test application

A Wagtail example for testing/development is bundled in this repo (find it at `tests/testapp`).

You can interact with this application inside your virtual environment using the `testmanage.py` script as you would a normal Django/Wagtail app.

For example, to bring up a development server on port `8000`, run:

```shell
python testmanage.py runserver 0:8000
```

If you have bootstrapped your environment with `tox`, there will be a default admin user (username: `admin`, password: `changeme`) available.

## Working with your own application

If you already have an application you'd like to use when developing Wagtail AI, you can install the package directly from source alongside it using `flit`:

```
# Install flit
python -m pip install flit
# Change directory to where you have cloned the wagtail-ai repo
cd wagtail-ai
# Install the package using 'symlink' mode so you can change the code without having to reinstall it
flit install -s
```

## Building frontend assets

Frontend assets (React components, admin scripts, custom CSS) are bundled using Webpack. A Node.js environment is required to install and run the dependencies required to build these assets. We recommend [`nvm`](https://github.com/nvm-sh/nvm#install--update-script) for installing and using Node.js locally:

```shell
nvm install 20
npm ci
```

If you are using the devcontainer, `node` and all relevant packages are already available.

Assets can then be built with:

```shell
npm run build
```

or in 'watch' mode with:

```shell
npm run start
```

## pre-commit

This project uses [pre-commit](https://github.com/pre-commit/pre-commit) to help keep to coding standards by automatically checking your commits.

If you are using the devcontainer, this is automatically configured. In other environments run:

```shell
# go to the project directory
cd wagtail-ai
# initialize pre-commit
pre-commit install

# Optional, run all checks once for this, then the checks will run only on the changed files
git ls-files --others --cached --exclude-standard | xargs pre-commit run --files
```

## Running tests

You can run tests using `tox`:

```shell
tox
```

or, you can run them for a specific environment `tox -e python3.11-django4.2-wagtail7.1` or specific test
`tox -e python3.11-django4.2-wagtail7.1-sqlite wagtail-ai.tests.test_file.TestClass.test_method`

## Building the documentation

Documentation for this package is built using `mkdocs`. These are automatically built by ReadTheDocs when pushed to Github, but you can build them yourself locally by:

```
# Installing the package with docs depdendencies
pip install -e .[docs] -U
# Build the docs
mkdocs build
```
