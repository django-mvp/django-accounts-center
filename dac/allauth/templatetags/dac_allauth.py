"""Template filters for the allauth overview cards.

The cards read what they need off ``user``, which the page they render on
already has. Two of the things they say about a person cannot be phrased as an
attribute lookup, and those are here. Both take a queryset the card already
walks and answer one question about it; neither fetches anything itself.

They live with the integration rather than in the core app because they are
about allauth's models, and the core app does not know allauth exists
(constitution Article XI).
"""

from django import template

register = template.Library()


@register.filter
def unverified_count(emailaddresses):
    """How many of ``emailaddresses`` are unverified.

    Usage: ``{{ user.emailaddress_set.all|unverified_count }}``.

    The email card carries this as a badge, and a template cannot count a
    subset of the list it is looping over.
    """
    return sum(1 for address in emailaddresses if not address.verified)


@register.filter
def has_second_factor(authenticators):
    """Whether ``authenticators`` holds a factor a person signs in with.

    Usage: ``{% if user.authenticator_set.all|has_second_factor %}``.

    Recovery codes are excluded deliberately. allauth stores them as an
    authenticator, but they are the way back in when the second factor is
    unavailable — an account holding only those has not turned two-factor
    sign-in on, and should not be told that it has.
    """
    from allauth.mfa.models import Authenticator

    signs_in_with = (Authenticator.Type.TOTP, Authenticator.Type.WEBAUTHN)
    return any(authenticator.type in signs_in_with for authenticator in authenticators)
