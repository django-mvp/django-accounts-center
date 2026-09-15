"""What the allauth overview cards know about the person looking at them.

One tag, ``{% account_summary as account %}``, answers the whole page. The
cards are template blocks with no view behind them, so anything they say has to
be reachable from the template — and a filter per question grows a new filter
every time a card learns to say something new. A single object grows a field
instead, and the card reads it the way it reads any other context.

An optional allauth app that is not installed is reported as ``None`` rather
than an empty section, so a card can tell "this project has no two-factor app"
from "this person has not set one up". Those are different sentences and only
one of them belongs on the page::

    {% if account.mfa %}          {# the app is installed #}
      {% if account.mfa.enabled %} … {% endif %}
    {% endif %}

Every collection is materialised here rather than left as a queryset, so a card
reading one twice does not ask the database twice.
"""

from dataclasses import dataclass

from django import template
from django.contrib.auth.models import AbstractBaseUser
from mvp.utils import app_is_installed

register = template.Library()


@dataclass(frozen=True)
class SocialAccounts:
    """The third-party accounts a person signs in with."""

    accounts: list

    @property
    def count(self):
        return len(self.accounts)


@dataclass(frozen=True)
class TwoFactor:
    """The second factors on a person's account."""

    authenticators: list
    enabled: bool


@dataclass(frozen=True)
class Sessions:
    """A person's active sign-ins."""

    count: int


@dataclass(frozen=True)
class AccountSummary:
    """Everything the cards say about one person.

    Add a field here when a card learns to say something new. ``social``,
    ``mfa`` and ``sessions`` are ``None`` when their allauth app is not
    installed.
    """

    emails: list
    unverified_email_count: int
    has_password: bool
    social: SocialAccounts | None
    mfa: TwoFactor | None
    sessions: Sessions | None

    @property
    def primary_email(self):
        return next((address for address in self.emails if address.primary), None)


def _two_factor(user) -> TwoFactor:
    """Recovery codes are excluded from ``enabled`` deliberately.

    allauth stores them as an authenticator, but they are the way back in when
    the second factor is unavailable. An account holding only those has not
    turned two-factor sign-in on, and a card saying otherwise would tell
    someone they are protected when they are not.
    """
    from allauth.mfa.models import Authenticator

    authenticators = list(user.authenticator_set.all())
    signs_in_with = (Authenticator.Type.TOTP, Authenticator.Type.WEBAUTHN)
    return TwoFactor(
        authenticators=authenticators,
        enabled=any(a.type in signs_in_with for a in authenticators),
    )


@register.simple_tag(takes_context=True)
def account_summary(context):
    """Usage: ``{% account_summary as account %}``.

    Returns ``None`` for an anonymous visitor, so a card drawn outside the
    signed-in area renders nothing rather than raising.
    """
    user = context.get("user")
    if not isinstance(user, AbstractBaseUser) or not user.is_authenticated:
        return None

    emails = list(user.emailaddress_set.all())
    return AccountSummary(
        emails=emails,
        unverified_email_count=sum(1 for address in emails if not address.verified),
        has_password=user.has_usable_password(),
        social=(
            SocialAccounts(accounts=list(user.socialaccount_set.all()))
            if app_is_installed("allauth.socialaccount")
            else None
        ),
        mfa=_two_factor(user) if app_is_installed("allauth.mfa") else None,
        sessions=(Sessions(count=user.usersession_set.count()) if app_is_installed("allauth.usersessions") else None),
    )
