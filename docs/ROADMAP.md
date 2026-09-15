# Roadmap — django-accounts-center

**Date:** 2026-07-27 · Revised 2026-09-15

This document was designed against [GOALS.md](../GOALS.md). See also [CONTEXT.md](../CONTEXT.md) for
domain terminology and [CONSTITUTION.md](../CONSTITUTION.md) for project standards.

Much of what follows is partly built. Each item says what exists today, so the sequence reads as
the whole build rather than as a list of gaps.

## Versioning

Releases are gated on goal importance, not on a count of features.

| Version | Gate |
|---|---|
| `0.7.x` | The current line. Fixes and additive work while the Essential goals are still open. |
| **`0.8.0`** | **All Essential goals delivered.** The framework is complete: three page layouts and a documented, reliable way to integrate against them. |
| `0.8.x` → `0.9.x` | Advance the Expected goals, at whatever granularity the work takes. Patches are fixes. |
| **`1.0.0`** | **All Expected goals delivered.** The complete, dependable release, and the point the integration contract becomes a public API. |
| `1.x` | Stable line. Non-breaking fixes and additive features only. |
| `2.0` | Next major. Breaking changes. |

Two rules this table does not show. A goal is not one minor release: some take several, and one
minor can move two goals at once. And once `1.0` ships, a breaking change never goes out as `1.x`
— it waits for the next major.

Aspirational goals may be developed against `2.0` or `1.x` as required.

This repo published `0.7.0` before its goals were recorded, so the standard `0.1.0` Essential gate
has been mapped onto the next minor rather than applied literally.

## Essential goals: v0.8.0

The framework itself, and a way to build against it that works and is written down. Most of the
framework is now django-mvp's: 0.22 gave it an Account Center with a landing page, a layout, a
menu any installed app can add to, and an includable URLconf. What is left here is the part
specific to accounts — the branded entrance page, and the contract an integration builds against.
No integration is required to reach this release, and none of it is specific to one.

### R1 — The entrance page

*delivered in [#19](https://github.com/django-mvp/django-accounts-center/issues/19), [#20](https://github.com/django-mvp/django-accounts-center/issues/20) · advances G2*

A full-screen page holding a single centered card, for anything a signed-out visitor sees. Built
from django-mvp's entrance component rather than restyled here.

This is the one layout that stays here. django-mvp ships an entrance page of its own, but the
branded card — the site logo above the content — is this package's, and a project gets it by
extending one template rather than assembling it.

It renders today, owned by the core app and reachable by any integration, and a page picks its
card width from django-mvp's own scale.

**Deliverables:**

- The card size accepts django-mvp's full scale rather than the interim two options
  ([#20](https://github.com/django-mvp/django-accounts-center/issues/20); the upstream scale
  shipped in django-mvp 0.16).
- Any entrance page that reads better at a different width moves onto it. None of the allauth
  pages does: they all read well at the default, and a width is worth setting on a page that
  needs one rather than on every page at once.

Serves G2.

### R2 — The management page

*delivered in [#42](https://github.com/django-mvp/django-accounts-center/issues/42) · advances G3, G6*

A single page style for any view where a person controls one aspect of their account, so a
management view written by one integration is indistinguishable in shape from one written by
another.

Per-request menu visibility is built: an integration attaches a check to an entry, and the entry
is absent for anyone it declines.

The page itself should be django-mvp's, and is not yet. Its account layout builds itself inside
`{% block content %}`, and allauth's stock templates all fill that same block — so a page routed
straight through it loses the navigation panel, quietly. This package keeps a layout of its own
until that is resolved upstream.

**Deliverables:**

- The management page is django-mvp's, and this package restates none of it
  ([django-mvp#358](https://github.com/django-mvp/django-mvp/issues/358)).

Serves G3 and G6.

### R3 — The account center dashboard

*feature · advances G4, G6*

The landing page of the Account Center: a dashboard of cards, each owned and rendered by the
integration that contributed it.

Both halves are done, and both came from moving onto django-mvp's page. A card is a block in that
page's own render, so it sees the request and the person making it and decides for itself whether
it applies. Card order follows `INSTALLED_APPS`, which is the ordinary Django rule for template
overrides rather than something to correct — an earlier version of this item asked for an ordering
this package defined, which would mean owning the page again.

Serves G4 and G6.

### R4 — Gated integrations

*feature · advances G1, G5, G8*

The machinery an integration plugs into: it is enabled by installing it and nothing else, it
contributes its menu entries, its cards and its pages through supported means, and a project
carries only the dependencies of what it enables.

Menu entries and cards are contributed through django-mvp's own extension points, and need
nothing from this package. URLs are the gap: the core app names each integration explicitly, so a
new one is unreachable without an edit to it.

The single-address deliverable is withdrawn. django-mvp mounts its Account Center wherever the
consuming project puts it, deliberately, and a path fixed here would contradict that. What this
package owes instead is that everything it serves sits beneath whichever prefix the project picks,
and that its own README, example project and tests agree on one.

**Deliverables:**

- An integration's pages are reachable purely as a consequence of it being installed.
- This repo demonstrates one prefix consistently, rather than three.
- The utilities an integration needs are deliberate, supported surfaces rather than incidental
  ones, and behave the same for every integration.

Serves G1, G5 and G8. What an integration must provide is documented in R5.

### R5 — The integration contract, documented

*feature · advances G7*

Someone building an integration can do it from documentation, without reading this package's
source or copying an existing integration and inheriting its accidents.

This closes the phase rather than opening it. A contract written before R4 settles would document
guesses. It now has to say which parts belong to django-mvp and which to this package, because an
author reaching for the wrong one finds nothing.

**Deliverables:**

- A reference covering every extension point, what each receives and what it is expected to
  return, naming the package that owns each.
- The rules that are not enforced by code, stated as rules — the `INSTALLED_APPS` ordering an
  integration must satisfy among them.
- A worked example an author can follow end to end.

Serves G7. Documentation is the whole of it — machine-checkable conformance is not planned.

## Expected goals: v1.0.0

Integrations, in the order they are wanted. Each is built on the framework above and none of them
changes it — where one does expose a gap, that is a correction to the Essential work rather than a
workaround inside the integration.

### R6 — The allauth integration

*Delivered · needs verification · advances G9*

Authentication, email, password, multi-factor, sessions and connected accounts, presented through
the three layouts. Styling is applied to the parts allauth composes its pages from rather than to
the pages themselves, so allauth features this package has never seen arrive already styled.

Built and shipping. What remains is durability: the set of parts to override is written down by
hand here, so when allauth adds one the check stays green and the new part renders unstyled —
precisely the failure the approach was chosen to avoid. Deriving that set from the installed
version of allauth, and recording a supported upstream range that matches what is verified, closes
the goal.

Serves G9.

### R7 — Profile management

*feature · advances G8*

Editing your own name, and whatever else a project counts as part of a person's profile. It is the
most common thing an account area does, the one capability every comparable product has, and this
package has no answer for it.

**Deliverables:**

- A person can edit their own profile from the Account Center.
- A project decides what a profile contains without forking the integration.

Serves G8. Does not cover public-facing profile pages, which are an application concern.

### R8 — A user controls their own data

*multi-feature · advances G10*

A person can see what the system holds about them, take a copy, and close the account. The
obligations behind it are not optional for a project operating in Europe.

**Deliverables:**

- A person can request and receive a copy of their own data.
- A person can delete their account, with the consequences stated before they confirm.
- Other integrations contribute the data they hold to both, rather than each shipping its own
  export.

Serves G10. Does not cover an operator-facing compliance console.

### R9 — Subscriptions

*multi-feature · advances G8*

Billing state in the Account Center: what a person is subscribed to, what they are paying, and the
controls to change it.

This is also the first integration whose pages genuinely apply to only some people, so it is the
real test of the per-request visibility built in R2 and R3.

**Deliverables:**

- A person can see and manage their subscription from the Account Center.
- The integration is gated and optional on the same terms as every other.

Serves G8. Does not cover operator-facing billing administration.
