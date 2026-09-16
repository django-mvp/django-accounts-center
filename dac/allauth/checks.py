"""Warn when a project has turned off allauth's safe GET defaults.

allauth defaults ``ACCOUNT_LOGOUT_ON_GET`` and ``ACCOUNT_CONFIRM_EMAIL_ON_GET``
to ``False`` for a reason: a GET request can be triggered by something other
than the person it's rendered to, and either setting turns that into a real
action. Signing out on GET lets an image tag or a link prefetch end somebody's
session; confirming an email on GET lets a mail gateway that prefetches links
consume the confirmation on the recipient's behalf. A project should not have
to know either of those to be safe from them, so this surfaces the mistake at
startup rather than in an incident.
"""

from django.conf import settings
from django.core import checks


@checks.register(checks.Tags.security)
def check_unsafe_get_settings(app_configs, **kwargs):
    warnings = []

    if getattr(settings, "ACCOUNT_LOGOUT_ON_GET", False):
        warnings.append(
            checks.Warning(
                "ACCOUNT_LOGOUT_ON_GET is True: signing out now responds to a "
                "GET request, so an image tag, a link prefetch, or a crawler "
                "can end a signed-in user's session without their action.",
                hint="Set ACCOUNT_LOGOUT_ON_GET = False (allauth's default) and require a POST to sign out.",
                id="dac_allauth.W001",
            )
        )

    if getattr(settings, "ACCOUNT_CONFIRM_EMAIL_ON_GET", False):
        warnings.append(
            checks.Warning(
                "ACCOUNT_CONFIRM_EMAIL_ON_GET is True: confirming an email "
                "address now responds to a GET request, so a mail gateway "
                "that prefetches links can consume the confirmation before "
                "the recipient ever opens it.",
                hint="Set ACCOUNT_CONFIRM_EMAIL_ON_GET = False (allauth's default) and require a POST to confirm.",
                id="dac_allauth.W002",
            )
        )

    return warnings
