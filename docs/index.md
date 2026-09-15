# Django Accounts Center

The account-management layer for [django-mvp](https://github.com/SamuelJennings/django-mvp)
projects. It gives a signed-in user one place to manage their account, and gives you a way to put
more things there as the project grows.

This package is not usable on its own. It renders on the django-mvp app shell (DaisyUI 5 +
Tailwind CSS v4 + django-cotton) and expects it.

## What it provides

- **An entrance layout.** Sign-in, sign-up and recovery pages render as a centered card with your
  site logo, outside the app shell.
- **An Account Center.** A management layout, a sub menu, and an overview page whose cards come
  from whatever you have installed.
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
                    "url_names": ("team_settings", "team_member_"),
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
- List your sub-pages' URL-name prefixes in `url_names` if the section has pages below its root.
  A page whose URL name starts with one of them is named as belonging to that section, so it gets
  the section's breadcrumb and, on a narrow screen, the section's name on the menu button. Leave
  `url_names` off and only the section root itself is recognised. A section whose entry is hidden
  from the current person is not named for them — breadcrumbs follow the menu they actually get.

## Installation

```bash
pip install django-accounts-center[allauth]
```

Settings, URLs and customisation are covered in the
[README](https://github.com/django-mvp/django-accounts-center#installation).
