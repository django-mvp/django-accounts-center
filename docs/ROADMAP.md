# Roadmap — django-accounts-center

**Date:** 2026-07-27

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

The framework itself: three page layouts, and a way to build against them that works and is
written down. No integration is required to reach this release, and none of it is specific to one.

### R1 — The entrance page

*feature · advances G2*

A full-screen page holding a single centered card, for anything a signed-out visitor sees. Built
from django-mvp's entrance component rather than restyled here.

It renders today, but only from inside the one integration that exists. Any other integration with
pages for signed-out visitors has nothing to inherit, and would have to extend a template named
for a package it has nothing to do with. The card is also one fixed size.

**Deliverables:**

- The page is owned by the core app and reachable by any integration.
- The card size is configurable. Where django-mvp's component cannot express what is needed, the
  shortfall is raised there rather than worked around here.
- Whatever renders entrance pages today reaches the shared page instead of defining its own, with
  no visible change to what it already produces.

Serves G2.

### R2 — The management page

*feature · advances G3, G6*

A single page style for any view where a person controls one aspect of their account. It carries
the sub menu, the breadcrumbs and the content area, so a management view written by one
integration is indistinguishable in shape from one written by another.

The page and its menu exist. What is missing is who each entry is for: menu entries are decided
once, when the process starts, from which apps are installed, so every signed-in person sees the
same menu. An integration whose pages apply to only some people has no way to say so, and the
person they do not apply to gets an entry leading somewhere useless.

**Deliverables:**

- Any integration can serve a management view through this page without special-casing.
- An integration declares, per request, whether each of its menu entries applies to the current
  visitor.
- Tests that an entry visible to one person is absent for another.

Serves G3 and G6.

### R3 — The account center dashboard

*feature · advances G4, G6*

The landing page of the Account Center: a dashboard of cards, each owned and rendered by the
integration that contributed it. The page collects whatever is installed without knowing what any
of it is.

Collection works. Visibility does not: a contributed card renders for everyone, so an integration
that applies to a subset of people shows the rest a card about something they do not have.

**Deliverables:**

- An integration declares, per request, whether each of its cards applies to the current visitor,
  and a card that does not apply is absent rather than empty.
- Card ordering is defined rather than an accident of installation order.
- Tests that a card visible to one person is absent for another.

Serves G4 and G6.

### R4 — Gated integrations

*feature · advances G1, G5, G8*

The machinery an integration plugs into: it is enabled by installing it and nothing else, it
contributes its menu entries, its cards and its pages through supported means, and a project
carries only the dependencies of what it enables.

Sub-apps are how this works today. That is an implementation choice, not a commitment, and the
work here is free to arrive at something better.

Two parts are missing. URLs are not contributed at all — the core names each integration
explicitly, so a new one is unreachable without an edit to the core. And there is no single
address for account management: the path is chosen by each consuming project, and this repo's
README, example project and tests each pick a different one.

**Deliverables:**

- An integration's pages are reachable purely as a consequence of it being installed.
- One predictable path for account management, owned by this package rather than by the consuming
  project, and consistent everywhere this repo demonstrates it.
- A stated position on where entrance pages sit relative to that path, given they serve anonymous
  visitors.
- The utilities an integration needs are deliberate, supported surfaces rather than incidental
  ones, and behave the same for every integration.

Serves G1, G5 and G8. What an integration must provide is documented in R5.

### R5 — The integration contract, documented

*feature · advances G7*

Someone building an integration can do it from documentation, without reading this package's
source or copying an existing integration and inheriting its accidents.

Today there is prose in the README, a glossary entry, and one worked example. The rules that are
not expressed in code are discoverable only by getting them wrong: the order an integration must
appear in relative to the package it integrates, what a contributed card may assume about the page
around it, what happens when two integrations contribute the same thing.

This closes the phase rather than opening it. A contract written before R4 settles would document
guesses.

**Deliverables:**

- A reference covering every extension point, what each receives and what it is expected to
  return.
- The rules that are not enforced by code, stated as rules.
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
