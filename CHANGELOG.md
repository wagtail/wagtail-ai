# AI Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.0] - 2025-10-09

### Added

- Page title and description generation with `AITitleFieldPanel` and `AIDescriptionFieldPanel`
- Image title and description generation during upload
- Contextual image alt text generation with `AIImageBlock` and `@ai_image_block`
- Qualitative content feedback
- Related pages suggestions support with `django-ai-core` vector index
- Unified interface for different LLM providers via `any-llm` library

### Changed

- `WAGTAIL_AI` settings now accepts a `PROVIDERS` key to configure different LLM providers using `django-ai-core` and `any-llm`
- `IMAGE_DESCRIPTION_BACKEND` setting replaced with `IMAGE_DESCRIPTION_PROVIDER`

## [2.1.2] - 2024-11-18

### Fixed

- Adjust rich text loading indicator to look correct in newer versions of Wagtail

## [2.1.1] - 2024-07-05

### Fixed

- Remove top-level `versioned_static` calls

## [2.1.0] - 2024-05-14

### Added

- Automatic alt-text generation for images (experimental) (Alex Morega)

### Fixed

- Add a `default_auto_field` to avoid creation of extra migration (Stefan Hammer)
- Documentation fixes (Kyle Bayliss)
- Improvements to pricing calculations in README (Fauzaan Gasim)

## [2.0.1] - 2024-01-19

### Changed

- Made `llm` a required dependency to simplify the installation process

## [2.0.0] - 2024-01-19

### Added

- New setting for specifying AI backends, with a new default backend using [`llm`](https://github.com/simonw/llm) (Tomasz Knapik)
- Support for many different LLMs such as GPT-4, local models, Mistral and Claude using [`llm` plugins`](https://llm.datasette.io/en/stable/plugins/directory.html) (Tomasz Knapik)
- Customisable text splitting backends (Tomasz Knapik)
- [More complete documentation](https://wagtail-ai.readthedocs.io/) (Tomasz Knapik)
- Custom prompts can now be managed through Wagtail admin (Ben Morse)

### Changed

- Removed Langchain dependency. Text splitting is now customisable and defaults to a vendorised version of Langchain's text splitter. (Tomasz Knapik)
- Various developer experience improvements. (Tomasz Knapik, Dan Braghis)
- Minimum supported versions increased to Wagtail 5.2, Django 4.2 and Python 3.11 (Dan Braghis)
- Improved how prompts are passed to the admin (Ian Meigh)

### Upgrade Considerations

#### Prompts managed in Wagtail admin

The `WAGTAIL_AI_PROMPTS` setting is no longer used. Prompts are now managed through the Wagtail admin under Settings -> Prompts.

Any custom prompts should be migrated to this new model, the `WAGTAIL_AI_PROMPTS` setting can then be removed.

### New Contributors/Thanks

- [@tm-kn](https://github.com/tm-kn) - AI backends/text splitting restructure
- [@zerolabl](https://github.com/zerolab) - support with developer tooling
- [@Morsey187](https://github.com/Morsey187) - frontend refinements and admin prompt management
- [@ianmeigh](https://github.com/ianmeigh) - improvements to admin integration

## [1.1.0] - 2023-03-10

### Added

- Support for customising prompts using the `WAGTAIL_AI_PROMPTS` setting

### Changed

- Content is now split based on token length before being sent to the API
- Significantly reduced bundle size (now using Draftail and Draft.js from Wagtail)
- Added better loading/error handling indicators

### New Contributors/Thanks

- [@tomdyson](https://github.com/tomdyson) for readme improvements, feature suggestions and a great demo in What's New in Wagtail

## [1.0.1] - 2023-03-06

### Changed

- Fixes an issue with 'completion' where it would throw a JS error trying to insert a new line.

## [1.0.0] - 2023-03-03

### Added

- Wagtail AI has appeared!


## [Unreleased]

<!-- TEMPLATE - keep below to copy for new releases -->
<!--


## [x.y.z] - YYYY-MM-DD

### Added

- ...

### Changed

- ...

### Removed

- ...

-->
