"""Menu definitions for django-accounts-center.

``AccountCenterMenu`` is the sub menu shown beside every Account Center page.
django-mvp declares it and ships its Overview entry; this package re-exports it
so integration sub-apps (``dac.allauth``, future ``dac.stripe``, …) can append
their own labelled ``MenuGroup`` from their ``menus.py``, and the menu grows
with the integrations the host project installs.

Declaring a second menu of the same name here is not an option, and not merely
a duplication: django-flex-menus holds every menu in one tree and looks one up
by name, so two claimants make the name unresolvable and every page that
renders the menu raises.
"""

from mvp.menus import AccountCenterMenu

__all__ = ["AccountCenterMenu"]
