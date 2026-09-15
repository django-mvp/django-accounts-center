# GOALS — django-accounts-center

Enduring goals this project pursues. Identity lives in the README; when work happens and which
release delivers it lives in the roadmap — this file names no versions. A goal is a capability
or quality you steer toward, not a task you complete: its id is stable, its importance is a tag
that can change, and whether it has been addressed enough is judged through the roadmap, specs,
and review rather than the goal itself.

**Importance** — `Essential`: not worth adopting without it · `Expected`: a complete,
dependable version is expected to have it · `Aspirational`: a genuine want whose absence never
makes the package incomplete.

**Status** — unmarked means accepted and live · `draft`: captured, not yet refined ·
`rejected`: decided against, kept with a reason and an ADR link when it's a design stance.

| ID | Goal | Importance | Status | Notes |
|----|------|------------|--------|-------|
| G1 | **Zero-wiring integration** — an integration is enabled by adding its app to `INSTALLED_APPS` and nothing else. Its menu, card, and views appear on their own. | Essential | | |
| G2 | **A shared entrance layout** — sign-in, sign-up, and recovery share one branded layout that no integration reimplements. | Essential | | |
| G3 | **A shared management layout** — every account-management page an integration serves looks and behaves the same. | Essential | | |
| G4 | **A pluggable account dashboard** — one overview that assembles itself from whichever integrations are active. | Essential | | django-mvp provides the page and the mechanism; this package contributes cards to it. |
| G5 | **One address for account management** — every integration's management views live beneath a single predictable path. | Essential | | The path is the consuming project's to choose, by where it mounts the two URLconfs. What this package guarantees is that its integrations all sit beneath whichever one is chosen. |
| G6 | **Per-user relevance** — menu entries and cards appear only when they apply to the person looking at them, not merely when the app is installed. | Essential | | |
| G7 | **A documented integration contract** — a developer can build an integration for their own app from the documentation, without reading this package's source. | Essential | | |
| G8 | **One dependency, enabled per project** — commonly needed integrations ship in-tree, so a project installs one package and turns on what it uses. | Essential | | |
| G9 | **Complete allauth coverage** — every allauth feature and configuration an adopter enables is presented, including features allauth adds in later releases. | Expected | | |
| G10 | **A user controls their own data** — review, export, and deletion are reachable from the accounts center. | Expected | | Supports GDPR compliance. May arrive through an integration rather than first-party views. |
| G11 | **A conformance kit for integration authors** — importable tests that verify an integration gates, mounts, and renders correctly. | Aspirational | draft | 2026-07-27 — documentation is sufficient today. Revisit when enough integrations ship in-tree to need a shared machine gate. |

_Written 2026-07-27. Revise as the goals change._
