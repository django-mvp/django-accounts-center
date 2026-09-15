# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Removed

- **BREAKING: this package no longer provides an Account Center.** django-mvp
  0.22 ships one — a landing page, a layout, a menu any installed app can add
  to, and an includable URLconf — and this package now fills that in rather
  than keeping a second version of it. What it still authors is the part
  django-mvp has no business knowing about: the allauth management pages, the
  branded entrance card, and its icon pack.

  Gone with it: `dac.views.AccountCenterView` and the `dac/account_center.html`
  it rendered, the `account-center` route in `dac.urls`, and the
  `dac_overview_template` / `dac_overview_context` pair on `AppConfig`.

  **On upgrade**, mount django-mvp's URLconf beside this package's, at the same
  prefix — the prefix is yours to choose, and django-mvp leaves it that way on
  purpose:

  ```python
  urlpatterns = [
      path("accounts/", include("mvp.urls")),
      path("accounts/", include("dac.urls")),
  ]
  ```

  An app contributing an overview card stops declaring those two `AppConfig`
  attributes and ships its own `mvp/account/overview.html` instead, extending
  that same name and adding to `{% block account.cards %}` through
  `{{ block.super }}`. A card is a block in the page's own render, so `user`
  and the request are already in scope and nothing is passed to it. The
  contributing app must be listed **before `mvp`** in `INSTALLED_APPS`, or the
  template loader never reaches its copy. A project that subclassed
  `dac.views.AccountCenterView` subclasses `mvp.views.AccountCenterView`.

- **BREAKING: the stylesheet and the front-end build that produced it.**
  `dac/static/css/dac.css`, `assets/tailwind.css`, `package.json` and its lock
  file are gone, and so is the Node toolchain. The visual layer belongs to
  django-mvp, and this package now composes its components and the DaisyUI
  utilities behind them rather than shipping CSS of its own.

  The build existed to carry two rules waiting on upstream fixes. Both landed,
  so both rules went: inline links in allauth's body copy are styled by
  django-mvp's `prose`, which takes its colours from the active theme, and the
  help-text spacing is django-mvp's own.

  **On upgrade**, nothing, unless your project linked `css/dac.css` itself or
  overrode `{% block styles %}` to load it. Every page reaches django-mvp's
  stylesheet by leaving that block alone. A project running its own Tailwind
  build no longer needs this package's templates as a source, because it
  introduces no class django-mvp's stylesheet does not already carry.

  The package also stopped shipping `dac/static/brand/`, which held a logo and
  an icon that nothing referenced and that shadowed django-mvp's own — an app
  listed before `mvp` wins the static path, so installing this package quietly
  replaced a project's brand mark.

- **BREAKING: the breadcrumb trail on Account Center pages, and everything
  behind it.** `dac.menus.get_active_section`, the `{% account_section %}`
  tag, the trail the layout drew, and the `url_names` entries in a menu item's
  `extra_context` that existed only to feed it. A menu entry that still
  declares `url_names` is simply ignored. Nothing replaces this here.

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

- **The management pages keep a layout of this package's own, for now.** They
  should render through django-mvp's account layout like everything else, and
  cannot yet: that layout builds itself inside `{% block content %}`, and
  allauth's stock templates all fill that same block. Django treats a nested
  block in a child as an override, so routing an allauth page through the
  layout drops the navigation panel beside it — on a page that still returns
  200, which is the worst way for it to fail. Raised at
  [django-mvp#358](https://github.com/django-mvp/django-mvp/issues/358), and
  `dac/base.html` goes when it closes.

### Added

- `{% account_summary as account %}`, one tag carrying everything the allauth
  cards say about the person looking at them. A card is a template block with
  no view behind it, so what it can say is bounded by what a template can ask,
  and a filter per question grows a filter every time a card learns to say
  something new. The object grows a field instead.

  An optional allauth app that is not installed is reported as `None` rather
  than an empty section, so `{% if account.mfa %}` asks whether the project has
  two-factor at all and `account.mfa.enabled` asks whether this person turned
  it on. Those are different sentences and only one belongs on a page.

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
