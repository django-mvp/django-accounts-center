"""Account Center menu contribution for the test integration app.

Proves the developer-facing contract this feature rests on: an app outside
the core package attaches a visibility check to the entries it contributes
(``flex_menu.MenuItem``'s own ``check`` argument — see plan.md, "What this
plan deliberately does not do"), and the Account Center asks it per request
while building the menu for whoever is looking.

flex-menus autodiscovers ``menus`` modules from installed apps
(``flex_menu/apps.py:9``), so nothing else imports this module.
"""

from django.utils.translation import gettext_lazy as _
from flex_menu import MenuItem
from mvp.menus import MenuGroup

from dac.menus import AccountCenterMenu

#: Group name whose members the "gated" entry's visibility check applies to.
GATED_GROUP_NAME = "testapp-gated"


def _visible_to_gated_group(request, **kwargs):
    """Visibility check for the "gated" entry: membership in a group.

    ``getattr`` rather than ``request.user`` directly: some structural tests
    render ``dac/base.html`` through a bare ``RequestFactory`` request with no
    ``AuthenticationMiddleware`` in the chain, so ``request`` may carry no
    ``user`` at all (not even ``AnonymousUser``). That is a rendering-harness
    artifact, not the "no anonymous case" the Account Center itself needs to
    answer for (D7) — the page is behind a sign-in requirement in every real
    request.
    """
    user = getattr(request, "user", None)
    if user is None:
        return False
    return user.groups.filter(name=GATED_GROUP_NAME).exists()


AccountCenterMenu.append(
    MenuGroup(
        name="testapp",
        extra_context={"label": _("Test App")},
        children=[
            MenuItem(
                name="gated",
                view_name="testapp_gated",
                extra_context={"label": _("Gated")},
                check=_visible_to_gated_group,
            ),
            MenuItem(
                name="ungated",
                extra_context={"label": _("Ungated")},
            ),
            MenuItem(
                name="sectioned",
                view_name="testapp_settings",
                extra_context={
                    "label": _("Settings"),
                },
            ),
        ],
    )
)
