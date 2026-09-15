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
(`AccountCenterMenu`, the `account-center` URL name). The plural exists only in
the package name and should not spread into new code.

The area itself is django-mvp's: it ships the landing page, the layout, the
menu and the URLconf, and this package fills them in.

- `mvp/urls.py` — the landing page, mounted by the project at its own prefix
- `dac/urls.py` — the installed integrations' pages, mounted at the same prefix

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
- **Overview cards** — by shipping its own copy of the landing page's template

Installation decides whether a contribution **exists**. The request decides
whether it is **shown** — see
[ADR 0002](docs/adr/0002-account-center-visibility-is-per-request.md).

For menu entries the second half is built: an integration attaches a
**visibility check** to an entry it wants shown to only some people, and the
Account Center asks it while building the menu for whoever is looking. A card
answers the same question in its own template, where the request and the
person making it are both in scope.

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

## Overview card

A card on the Account Center's landing page, contributed by shipping a copy of
that page's template, extending the same name, and adding to its card block
through `{{ block.super }}`. Django resolves a same-name extends to the next
template along the loader path, so several apps chain and the chain ends at
django-mvp's own copy. A contributing app must be listed before `mvp` in
`INSTALLED_APPS` or the loader never reaches it.

A card is a block in the page's own render, sharing its context — `user` and
everything the project's context processors provide are already there, and
nothing is passed to it. There is no attribute to declare and no registry.

What a card can say is bounded by what a template can ask, so an integration
whose cards need more than attribute lookups gives itself one tag returning one
object rather than a filter per question. `dac.allauth` does this with
`{% account_summary as account %}`, and reports an optional app that is not
installed as `None` so a card can tell an absent feature from an empty one.

The worked example is `dac/allauth/templates/mvp/account/overview.html`, with
its tag in `dac/allauth/templatetags/dac_allauth.py`.

## Entrance layout

The layout for pages shown to anonymous users — login, signup, password reset,
sign-in codes. Renders as a centered card with the site logo and no app shell.

The core package owns it, in two files:

- `dac/templates/dac/entrance.html` — the page an app extends. Carries the mvp
  base shell, the messages region and `{% block content %}`
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
django-flex-menus. django-mvp declares the menu and registers its Overview
item. Each integration appends its own labelled `MenuGroup`, so the menu
reflects the integrations a project installs.

`dac/menus.py` re-exports it from `mvp.menus`, so `dac.menus.AccountCenterMenu`
and `mvp.menus.AccountCenterMenu` are one object. Declaring a second menu of
that name here would not shadow django-mvp's — django-flex-menus keeps one tree
and resolves by name, so two claimants make the name unresolvable and every
page rendering the menu raises.

## Icon pack

`DAC_ICONS`, the django-easy-icons pack this package registers on top of
django-mvp's `BS5_ICONS`. Comma-separated keys register aliases for one glyph
(`"mfa, two_factor, security"`). It holds only names `BS5_ICONS` does not — a
key in both packs is reported as a collision, and the Account Center's own
`account_center` and `overview` belong to django-mvp.

`dac/icons.py`

Distinct from the **provider icons** in
`dac/allauth/templates/icons/*.svg` — brand SVGs for the ten social providers,
rendered by `provider.html` through a django-easy-icons `"svg"` renderer keyed by
allauth's provider id.

## Stylesheet

django-mvp's, and the only one. This package ships no CSS and no build to
produce any: it composes mvp's components and the DaisyUI utilities behind
them, so a class used here has to be one mvp's own stylesheet already carries
(constitution Article XVII).

Every page reaches it by leaving `{% block styles %}` alone.
`tests/test_architecture.py` fails on a `.css` file under the package, on a
`package.json` at the root, and on any template overriding that block — an
unstyled page is not an error, so nothing else would notice.
