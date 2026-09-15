"""Menu definitions for django-accounts-center.

``AccountCenterMenu`` is the sub menu shown on every Account Center page
(rendered by ``dac/base.html``). django-mvp declares it and ships its Overview
entry; this package re-exports it so integration sub-apps (``dac.allauth``,
future ``dac.stripe``, …) can append their own labelled ``MenuGroup`` from
their ``menus.py``, and the menu grows with the integrations the host project
installs.

Declaring a second menu of the same name here is not an option, and not merely
a duplication: django-flex-menus holds every menu in one tree and looks one up
by name, so two claimants make the name unresolvable and every page that
renders the menu raises.

Group items may declare ``url_names`` in ``extra_context`` — a tuple of
URL-name prefixes identifying their sub-pages — which breadcrumbs use to
resolve the active section on pages below a section root.
"""

from mvp.menus import AccountCenterMenu

__all__ = ["AccountCenterMenu", "get_active_section"]


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
