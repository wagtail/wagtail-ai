# AI Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [next] - 2023-11-29

### Added

- New setting for specifying AI backends, with a new default backend using [https://github.com/simonw/llm](`llm`) (Tomasz Knapik)
- Customisable text splitting backends (Tomasz Knapik)
- More complete documentation (Tomasz Knapik)

### Changed

- Backends are now specified with the `WAGTAIL_AI` setting. Support for `WAGTAIL_AI_BACKENDS` has been removed. (Tomasz Knapik)
- Removed Langchain dependency. Text splitting is now customisable and defaults to a vendorised version of Langchain's text splitter. (Tomasz Knapik)
- Various developer experience improvements. (Tomasz Knapik, Dan Braghis)

### New Contributors/Thanks

- [@tm-kn](https://github.com/tm-kn) - AI backends/text splitting restructure
- [@zerolabl](https://github.com/zerolab) - support with developer tooling

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
