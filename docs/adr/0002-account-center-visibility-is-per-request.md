# ADR 0002 — Account Center visibility is resolved per request

**Status:** accepted, implemented for menu entries

## Decision

Menu entries and overview cards answer one question per request: *should this appear for the
person looking at it, right now?*

Installation decides whether a contribution **exists**. The request decides whether it is
**shown**. Both halves are required — an integration that is installed is not thereby visible to
everyone.

The obligation sits on the integration. Each one declares, per request, whether each of its menu
entries and each of its cards applies to the current visitor, and a card that does not apply is
suppressed rather than rendered empty.

## Why

Most integrations worth bundling carry per-user state. A billing area means nothing to someone on
no plan. A team area means nothing to someone in no team. An integration whose pages apply to some
users has no way to say so if visibility is decided once at startup, and the person it does not
apply to gets a card or a menu entry leading somewhere useless.

That failure undermines the thing the framework promises. If adding an app to `INSTALLED_APPS` is
the whole wiring step, then the framework has to be the one that knows who a contribution is for.
Pushing the decision into each integration's views means every integration reimplements it and the
menu still lies.

The cost is accepted: every integration author implements one more hook, and the Account Center
pays a per-request cost it would not pay for a static menu. Visibility was considered as an
install-time-only concern and rejected. It is cheaper and it is wrong — a menu that lists things
you cannot use is worse than a shorter menu.

## State

Implemented for menu entries. An integration passes django-flex-menus' own `check` argument to a
`MenuItem` it contributes from its `menus.py` — a callable that takes the request and returns
whether that entry applies to the person making it. django-flex-menus evaluates `check` while
building the menu for each request, so two people loading the same page are answered separately,
and an entry whose check returns false is absent from the rendered tree. django-flex-menus already
hides a group left with no visible children, so a section with nothing left in it loses its
heading along with its entries — this package relies on that rather than reimplementing it. An
entry that declares no check stays visible whenever its integration is installed, exactly as
before this decision existed, so an existing integration needs no change to keep working.

A check that raises is not caught. The error surfaces as an error rather than being read as "does
not apply", because an entry that silently disappears leaves a developer with a missing menu item
and no stack trace, and swallowing the exception would also hide genuine failures in the
integration's own data access.

Breadcrumbs follow visibility rather than working around it. A section is named from the menu the
current person actually gets, so someone who opens a page whose entry is hidden from them gets no
section crumb. Naming it anyway would mean this package re-deriving navigation state that
django-flex-menus already owns, and that is not a layer worth carrying here. The gaps that make the
alternative tempting are filed upstream (django-flex-menus #34 and #35), and a template-based
breadcrumb is tracked on this repo's tracker.

Cards are unchanged by this decision, and were settled separately when the landing page moved to
django-mvp: a card is a block in that page's own render, so it sees the request and the person
making it and decides for itself whether it applies. Both halves of R3 are done.

The goal is G6. The work is R2 in the roadmap, in the Essential phase.

## Revisit if

Per-request evaluation shows up as a measurable cost on Account Center page loads that caching
cannot absorb, or a pattern emerges where integrations consistently want the same visibility rule
and would be better served by declaring it once than by answering per request.
