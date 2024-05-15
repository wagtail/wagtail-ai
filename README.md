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
* Automatically generate alt-tags for your uploaded images
* Work with multiple LLM providers including local models, OpenAI, Mistral, Claude and many others

## Demos

### Rich-text integration

https://user-images.githubusercontent.com/27112/223072938-8cb5ccff-4835-489a-8be4-cca85001885e.mp4

### Alt-text generation

https://github.com/wagtail/wagtail-ai/assets/27617/5ffd5493-b39c-4d38-bed8-fdd243920eb5

## Requirements & Costs

Wagtail AI supports [many different LLMs](https://wagtail-ai.readthedocs.io/latest/ai-backends/), with OpenAI models
available by default. To use these, you'll need an OpenAI account and an API key. There'll also be some cost involved.

For the OpenAI API used here (`gpt-3.5-turbo`), the [cost](https://openai.com/pricing) is

- $0.0005 per 1000 tokens for input tokens (prompt)
- $0.0015 per 1000 tokens for output tokens (answer)

Here is an estimated cost breakdown for the `correction` prompt on a 1000-word paragraph.

### We assume that:

- Prompt is 30 words and the existing paragraph is 1000 words (Input)
- Each word is 1.3 tokens (Tokens multiplier)
- We get back 1000 words back (Output)

### Then:

- **Input tokens :** (35 + 1000) x 1.3 = 1345.5 tokens.
- **Output tokens :** 1000 x 1.3 = 1300
- **Input tokens cost :** 1345.5 / 1000 * $0.0005 = $0.00067275
- **Output tokens cost :** 1300 / 1000 * $0.0015 = $0.00195
- **Total cost :** $0.00262275

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
