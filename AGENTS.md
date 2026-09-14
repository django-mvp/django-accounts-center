# AGENTS.md — Agent Configuration for django-accounts-center

<!-- Thin index only — bloat here = ignored instructions. Details live in the pointed-to files. -->

The account-management layer for django-mvp projects: an entrance layout, an Account Center
(management layout, sub menu, overview page), and the integration system that lets a third-party
app add its own pages to that Account Center. An **integration** is a gated sub-app a project
opts into through `INSTALLED_APPS` and nothing else. `dac.allauth` is the only one today, and it
restyles allauth by overriding its layouts and elements rather than forking its pages.

The framework is the product and allauth is its first integration, not the other way round. Goals
are recorded in `GOALS.md`.

## Stack & commands

- **Stack:** Python ≥ 3.12 / Django ≥ 5, Poetry-managed. Tailwind CSS v4 + DaisyUI 5 on django-mvp.
- **Install:** `poetry install && npm install`
- **Test:** `poetry run pytest`
- **Lint:** `poetry run ruff check .` (templates: `poetry run djlint .`)
- **Type-check:** `poetry run mypy .`
- **Build:** `poetry build`
- **Stylesheet:** `npm run build:css` — rebuild `dac/static/css/dac.css` after template changes
- **Screenshots (on demand, not a gate):** `poetry run pytest screenshots/`

## Agent skills

### Issue tracker

Issues tracked in GitHub Issues via the `gh` CLI. See `docs/agents/issue-tracker.md`.

### Triage labels

Default vocabulary (needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix).
See `docs/agents/triage-labels.md`.

### Domain docs

Single-context layout — `CONTEXT.md` at root, `docs/adr/` for decisions. See `docs/agents/domain.md`.

Read `CONTEXT.md` before naming anything. This repo has retired vocabulary still visible in
`specs/`, which is kept as a historical record and is not retrofitted.

### CI checks

Required status checks (exact names):

```
call-build / Code Quality
call-build / Security Scan
call-build / Build Package
call-tests / Test Python 3.12, Django 5.2
call-tests / Test Python 3.12, Django 6.0
call-tests / Test Python 3.13, Django 5.2
call-tests / Test Python 3.13, Django 6.0
```

CI is repo-native and calls the shared django-mvp reusable workflows, pinned to a release tag.

## Development workflow

Feature work follows a spec-driven process: spec → plan → tasks → implement → review → PR, with
`specs/NNN-slug/` directories generated per feature (there is no Spec Kit install in the repo).
Project standards and the quality bar live in `CONSTITUTION.md`.

Two things this repo will trip you up on if you skip the constitution:

- **Never fork an allauth page template.** Style through `allauth/elements/` instead.
  `tests/test_architecture.py` fails the build if you do. See `docs/adr/0001-*`.
- **Specs carry two audiences.** Every `spec.md` needs at least one `[Developer]` story and one
  `[End User]` story.
