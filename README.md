![wagtail-ai](https://user-images.githubusercontent.com/27112/223072917-8354f8f2-b687-44dd-9db7-33f2cc340233.png)

# Wagtail AI

Get help with your content using AI superpowers.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PyPI version](https://badge.fury.io/py/wagtail-ai.svg)](https://badge.fury.io/py/wagtail-ai)
[![ai CI](https://github.com/wagtail/wagtail-ai/actions/workflows/test.yml/badge.svg)](https://github.com/wagtail/wagtail-ai/actions/workflows/test.yml)

Wagtail AI integrates Wagtail with AI's APIs (think ChatGPT) to help you write and correct your content.

Right now, it can:

* Finish what you've started - write some text and tell Wagtail AI to finish it off for you
* Correct your spelling/grammar
* Let you add your own custom prompts
* Work with multiple LLM providers including local models, OpenAI, Mistral, Claude and many others

https://user-images.githubusercontent.com/27112/223072938-8cb5ccff-4835-489a-8be4-cca85001885e.mp4

## Requirements & Costs

Wagtail AI supports [many different LLMs](https://wagtail-ai.readthedocs.io/latest/ai-backends/), with OpenAI models available by default.

To use these, you'll need an OpenAI account and an API key. There'll also be some cost involved. For the OpenAI API used here, OpenAI charges $0.002 for 1,000 tokens (a word is about 1.3 tokens). Every token sent to the API, and every token we get back counts, so you can expect using 'correction' on 1,000 word paragraph to cost roughly:

* (1,000 * 1.3) + (35 * 1.3) (for the initial prompt) tokens sent to the API
* \+ (1,000 * 1.3) tokens received from the API
* = 2,645 tokens = $0.0053

## Links

- [Documentation](https://wagtail-ai.readthedocs.io/)
- [Changelog](https://github.com/wagtail/wagtail-ai/blob/main/CHANGELOG.md)
- [Contributing](https://wagtail-ai.readthedocs.io/latest/contributing/)
- [Discussions](https://github.com/wagtail/wagtail-ai/discussions)
- [Security](https://github.com/wagtail/wagtail-ai/security)

## Supported Versions

* Wagtail 5.2
* Django 4.2
* Python 3.11
