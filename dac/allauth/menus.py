"""allauth section of the Account Center menu.

Appends an "Email & Authentication" group to ``AccountCenterMenu``. Items for
optional allauth apps appear only when the app is installed.
"""

from django.utils.translation import gettext_lazy as _
from flex_menu import MenuItem
from mvp.menus import MenuGroup
from mvp.utils import app_is_installed

from dac.menus import AccountCenterMenu

_items = [
    MenuItem(
        name="email",
        view_name="account_email",
        extra_context={
            "label": _("Email"),
            "icon": "email",
        },
    ),
    MenuItem(
        name="password",
        view_name="account_change_password",
        extra_context={
            "label": _("Password"),
            "icon": "password",
        },
    ),
]

if app_is_installed("allauth.socialaccount"):
    _items.append(
        MenuItem(
            name="connections",
            view_name="socialaccount_connections",
            extra_context={
                "label": _("Connected accounts"),
                "icon": "social",
            },
        )
    )

if app_is_installed("allauth.mfa"):
    _items.append(
        MenuItem(
            name="mfa",
            view_name="mfa_index",
            extra_context={
                "label": _("Two-factor authentication"),
                "icon": "mfa",
            },
        )
    )

if app_is_installed("allauth.usersessions"):
    _items.append(
        MenuItem(
            name="sessions",
            view_name="usersessions_list",
            extra_context={
                "label": _("Sessions"),
                "icon": "sessions",
            },
        )
    )

AccountCenterMenu.append(
    MenuGroup(
        name="allauth",
        extra_context={"label": _("Email & Authentication")},
        children=_items,
    )
)
