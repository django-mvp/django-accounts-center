# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- **Every Account Center page raised when this package was installed alongside
  django-mvp 0.22.0.** That release gives django-mvp an Account Center of its
  own, and with it a menu named `AccountCenterMenu` — the name this package
  already used. django-flex-menus keeps every menu in one tree and looks one up
  by name, so a second claimant does not shadow the first: it leaves the name
  unresolvable, and every page that draws the menu raises rather than one of
  the two winning. The menu is now django-mvp's, re-exported from `dac.menus`
  so both import paths reach the same object and an integration's `append`
  calls are unchanged.

  The landing page's own entry is django-mvp's too, and reads **Overview**
  where it read "Account Center" before — the area's name is already above it.
  Nothing else about the menu changes.

### Changed

- `django-mvp` now requires `>=0.22`. The Account Center that release
  introduced is the one this package's menu and pages now belong to, so an
  earlier version no longer describes what this package needs.

- `DAC_ICONS` no longer registers `account_center` or `overview`. django-mvp's
  `BS5_ICONS` ships both, mapped to the same glyphs this pack used, and a name
  in both packs is reported as a collision. Either name still resolves and
  nothing on a page changes.

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
