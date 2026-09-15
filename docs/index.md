# Django Accounts Center

The account-management layer for [django-mvp](https://github.com/SamuelJennings/django-mvp)
projects. It gives a signed-in user one place to manage their account, and gives you a way to put
more things there as the project grows.

This package is not usable on its own. It renders on the django-mvp app shell (DaisyUI 5 +
Tailwind CSS v4 + django-cotton) and expects it.

## What it provides

- **An entrance layout.** Sign-in, sign-up and recovery pages render as a centered card with your
  site logo, outside the app shell.
- **Account-management pages.** allauth's email, password, two-factor, session and
  connected-account pages, rendered in django-mvp's Account Center, with a card apiece on its
  landing page.
- **An integration system.** The machinery that lets a third-party app add its own
  account-management pages to that Account Center.

## Integrations

An integration is a gated sub-app that teaches the Account Center about one third-party package.
You enable one by adding it to `INSTALLED_APPS`:

```python
INSTALLED_APPS = ["dac", "dac.allauth", ...]
```

From there the integration contributes its own labelled menu group, any overview cards it needs,
and its template overrides. What is installed decides which contributions exist.

Because every integration is gated, a project carries only the dependencies of the integrations it
turns on. Shipped today: `dac.allauth`, and it is the only one.

### Menu entries

Contribute entries from your own `menus.py`, appending a labelled group to `AccountCenterMenu`.
django-mvp declares the menu; `dac.menus` re-exports it, so the import below and
`from mvp.menus import AccountCenterMenu` reach the same object:

```python
from flex_menu import MenuItem
from mvp.menus import MenuGroup

from dac.menus import AccountCenterMenu

def _has_a_team(request, **kwargs):
    return request.user.teams.exists()

AccountCenterMenu.append(
    MenuGroup(
        name="teams",
        extra_context={"label": "Team"},
        children=[
            MenuItem(
                name="team_settings",
                view_name="team_settings",
                extra_context={
                    "label": "Settings",
                },
                check=_has_a_team,
            ),
        ],
    )
)
```

A few things to know before you write one:

- Pass `check=` for an entry that applies to only some people. It is a callable taking the request
  and returning whether the entry applies to whoever is making it, asked fresh for every request.
  An entry with no `check` stays visible whenever your integration is installed, exactly as it
  always has.
- Hiding is presentation only. Whether an entry shows in the menu and whether its page may be
  opened are separate questions — the URL still resolves whether or not the current person's menu
  shows the entry leading to it, so your view still owns who may open it.

## Installation

```bash
pip install django-accounts-center[allauth]
```

Settings, URLs and customisation are covered in the
[README](https://github.com/django-mvp/django-accounts-center#installation).

## Where this is going

[ROADMAP.md](ROADMAP.md) records what is built, what is next, and which parts of the Account
Center belong to django-mvp rather than to this package.
