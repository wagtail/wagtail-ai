![wagtail-ai](https://user-images.githubusercontent.com/27112/223072917-8354f8f2-b687-44dd-9db7-33f2cc340233.png)

# Wagtail AI

Get help with your content using AI superpowers.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/wagtail-ai.svg)](https://badge.fury.io/py/wagtail-ai)
[![ai CI](https://github.com/tomusher/wagtail-ai/actions/workflows/test.yml/badge.svg)](https://github.com/tomusher/wagtail-ai/actions/workflows/test.yml)

Wagtail AI integrates Wagtail with OpenAI's APIs (think ChatGPT) to help you write and correct your content.

Right now, it can:

* Finish what you've started - write some text and tell Wagtail AI to finish it off for you
* Correct your spelling/grammar

https://user-images.githubusercontent.com/27112/223072938-8cb5ccff-4835-489a-8be4-cca85001885e.mp4

## Requirements & Costs

You'll need a paid OpenAI account and an API key. There'll also be some cost involved. For the API used here, OpenAI charges $0.002 for 1,000 tokens (roughly 4 characters). Every token sent to the API, and every token we get baack counts, so you can expect using 'correction' on 1,000 word paragraph to cost roughly:

* (1,000 * 4) + (35 * 4) (for the initial prompt) tokens sent to the API
* +4,000 tokens received from the API
* = 8,140 tokens = $0.016

## The Future

Wagtail AI is very new. Here's some things we'd like to do:

* [ ] Streaming support - the API supports server-sent events, we could do the same
* [ ] A nice UI - it's a bit rough right now
* [ ] Reduce bundle size
* [ ] Internationalisation on text and support for different language prompts
* [ ] Find a better way to hook in to Draftail to do things like show progress bars/spinners.
* [ ] Add more AI behaviours and features - content recommendations, content based Q&A tools, better ways to direct the prompt.
* [ ] Tests!

If you're interested in working on these things, please do!

## Links

- [Documentation](https://github.com/tomusher/wagtail-ai/blob/main/README.md)
- [Changelog](https://github.com/tomusher/wagtail-ai/blob/main/CHANGELOG.md)
- [Contributing](https://github.com/tomusher/wagtail-ai/blob/main/CHANGELOG.md)
- [Discussions](https://github.com/tomusher/wagtail-ai/discussions)
- [Security](https://github.com/tomusher/wagtail-ai/security)

## Supported Versions

* Wagtail 4.0, 4.1 and 4.2

## Installation

- `python -m pip install wagtail-ai`
- Add `wagtail_ai` to your `INSTALLED_APPS`
- Add an `OPENAI_API_KEY = {api_key}` to your settings key, replacing `{api_key}` with your OpenAI API key.

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
