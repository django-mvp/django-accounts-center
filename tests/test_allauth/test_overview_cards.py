"""The allauth cards on the Account Center's landing page.

The page is django-mvp's. This package puts cards on it by shipping its own
``mvp/account/overview.html``, extending that same name and adding to the card
block — django-mvp's documented extension point. Django resolves the extends to
the next template of the name along the loader path, so the two chain, and
these tests cover that the chain holds and that each card says the right thing
about the person looking at it.

Nothing is passed to a card. Each reads what it needs off ``user``, which the
surrounding page already has, so a card that quietly stops finding its data
fails here rather than rendering an empty shell.
"""

import pytest
from allauth.account.models import EmailAddress
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
from allauth.mfa.totp.internal.auth import TOTP, generate_totp_secret
from django.urls import reverse

from tests.factories import UserFactory


def _overview(client, user):
    client.force_login(user)
    response = client.get(reverse("account-center"))
    assert response.status_code == 200
    return response


@pytest.mark.django_db
class TestCardsReachThePackagedPage:
    def test_the_chain_renders_both_templates(self, client):
        """django-mvp's landing page and this package's copy both render, which
        is what the same-name extends is for."""
        response = _overview(client, UserFactory())
        names = [template.name for template in response.templates if template.name]
        assert names.count("mvp/account/overview.html") == 2

    def test_every_card_for_an_installed_app_is_drawn(self, client):
        """One card per allauth app the test settings install."""
        content = _overview(client, UserFactory()).content.decode()
        for title in [
            "Email",
            "Password",
            "Connected accounts",
            "Two-factor authentication",
            "Sessions",
        ]:
            assert title in content


@pytest.mark.django_db
class TestEmailCard:
    def test_lists_the_addresses_on_the_account(self, client):
        user = UserFactory()
        EmailAddress.objects.create(user=user, email="first@example.com", primary=True, verified=True)
        EmailAddress.objects.create(user=user, email="second@example.com", verified=False)
        content = _overview(client, user).content.decode()
        assert "first@example.com" in content
        assert "second@example.com" in content

    def test_counts_the_unverified_addresses(self, client):
        user = UserFactory()
        EmailAddress.objects.create(user=user, email="ok@example.com", primary=True, verified=True)
        EmailAddress.objects.create(user=user, email="pending@example.com", verified=False)
        EmailAddress.objects.create(user=user, email="also@example.com", verified=False)
        assert "2 unverified" in _overview(client, user).content.decode()

    def test_says_nothing_is_on_record_when_there_is_no_address(self, client):
        user = UserFactory()
        user.emailaddress_set.all().delete()
        content = _overview(client, user).content.decode()
        assert "No email address on record." in content
        assert "unverified" not in content


@pytest.mark.django_db
class TestTwoFactorCard:
    def test_disabled_for_an_account_with_no_authenticator(self, client):
        content = _overview(client, UserFactory()).content.decode()
        assert "Add a second factor to make your account more secure." in content

    def test_enabled_once_an_authenticator_app_is_active(self, client):
        user = UserFactory()
        TOTP.activate(user, generate_totp_secret())
        content = _overview(client, user).content.decode()
        assert "Your account is protected by two-factor authentication." in content

    def test_recovery_codes_alone_do_not_count_as_a_second_factor(self, client):
        """Recovery codes are the way back in when the second factor is
        unavailable, so an account holding only those has not turned two-factor
        sign-in on and must not be told it has."""
        user = UserFactory()
        RecoveryCodes.activate(user)
        assert user.authenticator_set.filter(type=Authenticator.Type.RECOVERY_CODES).exists()
        content = _overview(client, user).content.decode()
        assert "Add a second factor to make your account more secure." in content


@pytest.mark.django_db
class TestPasswordCard:
    def test_reports_a_usable_password(self, client):
        content = _overview(client, UserFactory()).content.decode()
        assert "A password is set for your account." in content

    def test_reports_no_password_for_an_account_that_has_none(self, client):
        user = UserFactory()
        user.set_unusable_password()
        user.save()
        content = _overview(client, user).content.decode()
        assert "You have no password set." in content


@pytest.mark.django_db
class TestSessionsCard:
    def test_counts_the_active_sessions(self, client):
        """A signed-in person has one session, and the card pluralises."""
        content = _overview(client, UserFactory()).content.decode()
        assert "active session" in content
