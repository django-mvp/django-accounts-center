"""The summary the allauth overview cards read.

One tag answers the whole landing page, so these tests cover what it reports
about a person and — just as important — what it reports about the project. An
optional allauth app that is not installed comes back as ``None``, which is how
a card tells "this project has no two-factor app" from "you have not set one
up".

The cards that consume it are covered in ``test_overview_cards``.
"""

import pytest
from allauth.account.models import EmailAddress
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
from allauth.mfa.totp.internal.auth import TOTP, generate_totp_secret
from django.contrib.auth.models import AnonymousUser
from django.template import Context, Template

from dac.allauth.templatetags.dac_allauth import account_summary
from tests.factories import UserFactory

_TAG = Template("{% load dac_allauth %}{% account_summary as account %}{{ account.has_password }}")


def _summary(user):
    return account_summary({"user": user})


@pytest.mark.django_db
class TestEmails:
    def test_reports_the_addresses_on_the_account(self):
        user = UserFactory()
        EmailAddress.objects.create(user=user, email="first@example.com", primary=True, verified=True)
        EmailAddress.objects.create(user=user, email="second@example.com", verified=False)
        emails = {address.email for address in _summary(user).emails}
        assert emails == {"first@example.com", "second@example.com"}

    def test_counts_only_the_unverified(self):
        user = UserFactory()
        EmailAddress.objects.create(user=user, email="ok@example.com", primary=True, verified=True)
        EmailAddress.objects.create(user=user, email="pending@example.com", verified=False)
        EmailAddress.objects.create(user=user, email="also@example.com", verified=False)
        assert _summary(user).unverified_email_count == 2

    def test_names_the_primary_address(self):
        user = UserFactory()
        user.emailaddress_set.all().delete()
        EmailAddress.objects.create(user=user, email="second@example.com", verified=True)
        primary = EmailAddress.objects.create(user=user, email="first@example.com", primary=True, verified=True)
        assert _summary(user).primary_email == primary

    def test_no_primary_when_none_is_marked(self):
        user = UserFactory()
        user.emailaddress_set.all().delete()
        EmailAddress.objects.create(user=user, email="only@example.com", verified=False)
        assert _summary(user).primary_email is None


@pytest.mark.django_db
class TestPassword:
    def test_true_for_an_account_with_a_usable_password(self):
        assert _summary(UserFactory()).has_password is True

    def test_false_for_an_account_with_none(self):
        user = UserFactory()
        user.set_unusable_password()
        user.save()
        assert _summary(user).has_password is False


@pytest.mark.django_db
class TestTwoFactor:
    def test_disabled_when_nothing_is_set_up(self):
        assert _summary(UserFactory()).mfa.enabled is False

    def test_enabled_by_an_authenticator_app(self):
        user = UserFactory()
        TOTP.activate(user, generate_totp_secret())
        assert _summary(user).mfa.enabled is True

    def test_recovery_codes_alone_are_not_a_second_factor(self):
        """They are the way back in when the second factor is unavailable. An
        account holding only those has not turned two-factor sign-in on, and a
        card saying otherwise would tell someone they are protected when they
        are not."""
        user = UserFactory()
        RecoveryCodes.activate(user)
        summary = _summary(user)
        assert summary.mfa.authenticators
        assert all(a.type == Authenticator.Type.RECOVERY_CODES for a in summary.mfa.authenticators)
        assert summary.mfa.enabled is False

    def test_recovery_codes_beside_a_real_factor_still_count(self):
        user = UserFactory()
        TOTP.activate(user, generate_totp_secret())
        RecoveryCodes.activate(user)
        assert _summary(user).mfa.enabled is True


@pytest.mark.django_db
class TestOptionalAppsThatAreInstalled:
    """The test settings install socialaccount, mfa and usersessions, so each
    section is present — an empty one, not a missing one."""

    def test_every_section_is_reported(self):
        summary = _summary(UserFactory())
        assert summary.social is not None
        assert summary.mfa is not None
        assert summary.sessions is not None

    def test_an_installed_app_with_nothing_in_it_is_still_a_section(self):
        summary = _summary(UserFactory())
        assert summary.social.accounts == []
        assert summary.social.count == 0


@pytest.mark.django_db
class TestOptionalAppsThatAreNot:
    def test_a_missing_app_is_reported_as_absent_rather_than_empty(self, monkeypatch):
        """A card reads `None` here and draws nothing, which is different from
        drawing an empty card for a feature the project does not have."""
        import dac.allauth.templatetags.dac_allauth as module

        monkeypatch.setattr(module, "app_is_installed", lambda name: False)
        summary = _summary(UserFactory())
        assert summary.social is None
        assert summary.mfa is None
        assert summary.sessions is None
        # The sections that do not depend on an optional app still report.
        assert summary.has_password is True


@pytest.mark.django_db
class TestAnonymousVisitor:
    def test_reports_nothing_rather_than_raising(self):
        assert _summary(AnonymousUser()) is None

    def test_a_card_drawn_for_a_visitor_renders_empty(self):
        assert _TAG.render(Context({"user": AnonymousUser()})).strip() == ""

    def test_missing_user_in_context_reports_nothing(self):
        assert account_summary({}) is None
