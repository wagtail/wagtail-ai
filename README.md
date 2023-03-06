# Wagtail AI

Get a hand writing your content with AI super powers!

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/wagtail-ai.svg)](https://badge.fury.io/py/wagtail-ai)
[![AI CI](https://github.com/tomusher/wagtail-ai/actions/workflows/test.yml/badge.svg)](https://github.com/tomusher/wagtail-ai/actions/workflows/test.yml)

## Links

- [Documentation](https://github.com/tomusher/wagtail-ai/blob/main/README.md)
- [Changelog](https://github.com/tomusher/wagtail-ai/blob/main/CHANGELOG.md)
- [Contributing](https://github.com/tomusher/wagtail-ai/blob/main/CHANGELOG.md)
- [Discussions](https://github.com/tomusher/wagtail-ai/discussions)
- [Security](https://github.com/tomusher/wagtail-ai/security)

## Supported versions

- Python ...
- Django ...
- Wagtail ...

## Installation

- `python -m pip install wagtail-ai`
- ...

## Contributing

### Install

To make changes to this project, first clone this repository:

```sh
git clone https://github.com/tomusher/wagtail-ai.git
cd wagtail-ai
```

With your preferred virtualenv activated, install testing dependencies:

#### Using pip

```sh
python -m pip install --upgrade pip>=21.3
python -m pip install -e .[testing] -U
```

#### Using flit

```sh
python -m pip install flit
flit install
```

### pre-commit

Note that this project uses [pre-commit](https://github.com/pre-commit/pre-commit).
It is included in the project testing requirements. To set up locally:

```shell
# go to the project directory
$ cd wagtail-ai
# initialize pre-commit
$ pre-commit install

# Optional, run all checks once for this, then the checks will run only on the changed files
$ git ls-files --others --cached --exclude-standard | xargs pre-commit run --files
```

### How to run tests

Now you can run tests as shown below:

```sh
tox
```

or, you can run them for a specific environment `tox -e python3.8-django3.2-wagtail2.15` or specific test
`tox -e python3.9-django3.2-wagtail2.15-sqlite wagtail-ai.tests.test_file.TestClass.test_method`

To run the test app interactively, use `tox -e interactive`, visit `http://127.0.0.1:8020/admin/` and log in with `admin`/`changeme`.
