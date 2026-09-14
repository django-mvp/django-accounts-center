# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [v0.7.1] - 2026-08-06

### Added

- The entrance page is now part of the core package, at `dac/entrance.html`.
  Any installed app can give itself a signed-out page of its own — an
  invitation flow, say — by extending it and filling `{% block content %}`,
  instead of reaching into the allauth integration for a template. A page that
  wants a wider card overrides `{% block entrance %}` and nests its content
  inside a `<c-dac.entrance size="full">`. Anything else keeps the width
  entrance pages have today.

### Changed

- The allauth entrance layout no longer authors any chrome of its own. It maps
  allauth's blocks onto `dac/entrance.html`, and that is all it now contains.
  Its pages render as they did before.

- Dependency constraints now match what is verified. Django widens to
  `>=5.2,<7.0`, which is the range CI tests — the previous `<6.0` cap declared
  an install that pip would refuse while two green Django 6.0 checks said
  otherwise. `django-mvp` gains bounds (`>=0.15,<1.0`); it was previously
  unconstrained despite this package depending on its internals. The `allauth`
  extra pins to the major it is coupled to (`>=65.18,<66.0`), with matching
  caps on crispy-forms and crispy-tailwind.

### Fixed

- The test URL configuration mounted `allauth.urls` alongside `dac.urls`, which
  already includes it. Every allauth URL name was registered twice and resolved
  by last registration.

## [0.7.0]

Releases before this file existed are recorded in the
[GitHub releases](https://github.com/django-mvp/django-accounts-center/releases).
