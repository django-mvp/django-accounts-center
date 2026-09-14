"""Menu definitions for django-accounts-center.

``AccountCenterMenu`` is the internal sub menu shown on every Account Center
page (rendered by ``dac/base.html``). The core package registers only the
Overview item; integration sub-apps (``dac.allauth``, future ``dac.stripe``,
…) append their own labelled ``MenuGroup`` from their ``menus.py``, so the
menu grows with the integrations the host project installs.

Group items may declare ``url_names`` in ``extra_context`` — a tuple of
URL-name prefixes identifying their sub-pages — which breadcrumbs use to
resolve the active section on pages below a section root.
"""

from django.utils.translation import gettext_lazy as _
from flex_menu import Menu, MenuItem

AccountCenterMenu = Menu(
    name="AccountCenterMenu",
    children=[
        MenuItem(
            name="overview",
            view_name="account-center",
            extra_context={"label": _("Account Center"), "icon": "overview"},
        ),
    ],
)


def get_active_section(request):
    """Return the AccountCenterMenu section for ``request`` as a dict.

    Returns ``{"label": …, "url": …, "is_current": bool}`` — ``is_current``
    means the request is the section page itself (render the crumb as plain
    text), otherwise the request is a sub-page of the section (render the
    crumb as a link). Returns ``None`` on the overview page or when no
    section matches.

    Sections are the leaf items nested under a group (a ``MenuGroup`` such as
    ``allauth``'s "Email & Authentication"); the bare ``overview`` entry is
    excluded because it has no children of its own, not because of its name.
    ``process()`` already prunes anything not visible before this runs, and
    only attaches a child to its processed parent, so a processed item's
    ``.children`` and its inherited ``.leaves`` (anytree) walk exactly the
    request-visible tree — no separate walker is needed here.
    """
    processed = AccountCenterMenu.process(request)
    leaves = [leaf for group in processed.children if group.has_children for leaf in group.leaves]

    for item in leaves:
        if item.selected:
            return {
                "label": item.extra_context.get("label", item.name),
                "url": item.url,
                "is_current": True,
            }

    url_name = getattr(request.resolver_match, "url_name", None)
    if url_name:
        for item in leaves:
            for prefix in item.extra_context.get("url_names", ()):
                if url_name.startswith(prefix):
                    return {
                        "label": item.extra_context.get("label", item.name),
                        "url": item.url,
                        "is_current": False,
                    }
    return None
