"""Template tags for django-accounts-center."""

from django import template
from mvp.utils import app_is_installed as _app_is_installed

register = template.Library()


@register.filter
def app_is_installed(app_name):
    """Whether ``app_name`` is in ``INSTALLED_APPS``.

    Usage: ``{% if "allauth.mfa"|app_is_installed %}``.

    An overview card has to tell "this project has no two-factor app" from
    "this person has not set one up" — different sentences, and only one of
    them belongs on the page. A card is a template block with no view behind
    it, so the question has to be answerable from a template.

    django-mvp owns this: the function being wrapped is its own, and it is
    asked for there at django-mvp/django-mvp#355. This wrapper goes when that
    lands.
    """
    return _app_is_installed(app_name)
