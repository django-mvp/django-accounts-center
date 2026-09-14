# CONTEXT.md — domain glossary

The vocabulary this package uses for itself. When naming things in issues, specs,
tests, commits and code, use the terms defined here. Where a term has a synonym
that has drifted into use, the synonym is listed as **avoid** — not because it is
wrong in English, but because two names for one concept costs more than it saves.

---

## Account Center

The account-management area this package provides: an overview page plus the
management pages reachable from it, rendered inside the django-mvp app shell
with their own sub navigation. Which management pages exist depends on the
integrations a project installs. Today they all come from `dac.allauth`.

Singular **Account Center**, not "Accounts Center" — even though the distribution
is named `django-accounts-center`. The code is consistent on this
(`AccountCenterView`, `AccountCenterMenu`, the `account-center` URL name). The
plural exists only in the package name and should not spread into new code.

- `dac/views.py` — `AccountCenterView`, the overview page
- `dac/urls.py` — mounted at the URLconf root as `account-center`

**Avoid:** "accounts center", "user center", "profile area".

## Integration

A gated sub-app that teaches the Account Center about one third-party package.
`dac.allauth` is the only one today. The pattern is built for more, and Stripe
was the worked example when the design was set.

An integration is opted into individually through `INSTALLED_APPS`, so a project
only carries the dependencies of the integrations it actually uses. It lives at
`dac/<package>/` — a package directory beside the core app, not under a
container directory.

An integration may contribute any of:

- **URLs** — included conditionally from `dac/urls.py` via `app_is_installed()`
- **Menu items** — appended to `AccountCenterMenu` from its own `menus.py`
- **Overview cards** — through the two `AppConfig` hooks described below

Installation decides whether a contribution **exists**. The request decides
whether it is **shown** — see
[ADR 0002](docs/adr/0002-account-center-visibility-is-per-request.md).

For menu entries the second half is built: an integration attaches a
**visibility check** to an entry it wants shown to only some people, and the
Account Center asks it while building the menu for whoever is looking.
Overview cards are still decided once at startup from `app_is_installed()`,
so every signed-in person sees the same cards — that half stays decided, not
built.

URLs are a further exception to "the integration contributes it": `dac/urls.py`
names each integration explicitly, so a new integration is not reachable
without an edit to the core app.

**Avoid: "addon".** This was the earlier name. It survives in `specs-overview.md`,
which refers to a `dac.addons.allauth` import path that was never built, and
throughout `specs/001`–`011`, which are kept as the historical record and are not
retrofitted. The real module is `dac.allauth`, app label `dac_allauth`.

## Visibility check

An integration's per-request answer to whether one menu entry applies to the
person making the current request. It is a property of one entry, answered
fresh for every request, so two people loading the same page can be answered
differently.

An integration gives this answer by passing a callable to django-flex-menus'
own `check` argument on the `MenuItem` it contributes — there is no
package-specific API layered over it, only this name for the concept. A
check is optional: an entry that declares none stays visible whenever its
integration is installed, exactly as an entry without one always has.

`dac/menus.py`, `tests/testapp/menus.py` (the worked example). See
[ADR 0002](docs/adr/0002-account-center-visibility-is-per-request.md).

## Overview card hooks

Two optional attributes an `AppConfig` may define to contribute cards to the
Account Center overview page. `AccountCenterView.get_context_data()` walks every
installed app and collects them, so any app can contribute — not only a `dac.*`
integration.

- `dac_overview_template` — a template rendered inside the overview grid
- `dac_overview_context(request)` — returns extra context for that template

Defined at `dac/views.py:25-37`. The worked example is `dac/allauth/apps.py:20-57`.

## Entrance layout

The layout for pages shown to anonymous users — login, signup, password reset,
sign-in codes. Renders as a centered card with the site logo and no app shell.

The core package owns it, in two files:

- `dac/templates/dac/entrance.html` — the page an app extends. Carries the mvp
  base shell, the stylesheet link, the messages region and `{% block content %}`
- `dac/templates/cotton/dac/entrance.html` — the `<c-dac.entrance>` component:
  mvp's `<c-entrance>` card with the site logo above the slot

Any installed app reaches it with a bare `{% extends "dac/entrance.html" %}`,
without referencing a template that belongs to an integration.

## Manage layout

The layout for pages shown to signed-in users — email, password, MFA, sessions,
connected accounts. Renders inside the django-mvp shell via `dac/base.html`,
with the Account Center sub menu beside the content.

Today it exists only as an allauth layout override, at
`dac/allauth/templates/allauth/layouts/manage.html`, over the core
`dac/base.html` that every integration's management page is meant to reach.

Together with `base.html` these are the three layout overrides that
`tests/test_architecture.py::test_layouts_overridden` requires.

## Element

One of allauth's `{% element %}` partials — `button`, `field`, `panel`, `alert`,
`table` and so on. Overriding these is how the package restyles allauth: allauth's
own stock page templates keep doing the rendering, and every element they emit
resolves to DaisyUI markup.

There are 22, listed in `EXPECTED_ELEMENTS` in `tests/test_architecture.py`,
which fails if any override goes missing. They live in
`dac/allauth/templates/allauth/elements/`.

Elements are the reason the package tracks allauth features it has never heard
of: a new allauth page built from existing elements is styled on arrival.

## Page override

A fork of an allauth *page* template, as opposed to an element. These are the
thing the architecture is designed to avoid — see
[ADR 0001](docs/adr/0001-elements-first-allauth-integration.md).

Any page override must be listed in `PAGE_OVERRIDE_ALLOWLIST` in
`tests/test_architecture.py`, which currently holds exactly one entry
(`account/snippets/warn_no_email.html`). An unlisted fork fails the suite.

## Account Center menu

The sub navigation shown on every Account Center page, built on
django-flex-menus. The core package registers only the Overview item. Each
integration appends its own labelled `MenuGroup`, so the menu reflects the
integrations a project installs.

`dac/menus.py` — `AccountCenterMenu`

## Section

A top-level entry in the Account Center menu, used for breadcrumb resolution. A
menu item may declare `url_names` in its `extra_context` — a tuple of URL-name
prefixes identifying its sub-pages — so a breadcrumb can name the section a
sub-page belongs to.

`dac/menus.py:29-67` — `get_active_section()`, surfaced to templates as the
`{% account_section %}` tag.

## Icon pack

`DAC_ICONS`, the django-easy-icons pack this package registers on top of
django-mvp's `BS5_ICONS`. Comma-separated keys register aliases for one glyph
(`"mfa, two_factor, security"`).

`dac/icons.py`

Distinct from the **provider icons** in
`dac/allauth/templates/icons/*.svg` — brand SVGs for the ten social providers,
rendered by `provider.html` through a django-easy-icons `"svg"` renderer keyed by
allauth's provider id.

## Prebuilt stylesheet

`dac/static/css/dac.css`, the Tailwind v4 + DaisyUI 5 build shipped inside the
package so a consuming project needs no Tailwind toolchain of its own. Built from
`assets/tailwind.css` by `npm run build:css`, and rebuilt whenever templates
change.

A project running its own Tailwind build adds this package's templates as a
source instead, and overrides the `styles` block.
