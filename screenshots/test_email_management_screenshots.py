"""
Playwright screenshot tests for the allauth email management flow.

Covers T009 / Principle XIII: Multi-Viewport Screenshot Coverage.

6 page states × 2 viewports = 12 PNG files written to docs/_static/{tier}/.

Page states:
  - email-change-no-pending  : email_change.html (1 verified email, no pending change)
  - email-change-pending     : email_change.html (current email + pending new address)
  - email-change-no-email    : email_change.html (user with no email addresses)
  - email-multi-list         : email.html (2 addresses: 1 verified primary, 1 unverified)
  - email-verified-required  : verified_email_required.html (gate page, no auth required)
  - email-warn-no-email      : email.html (multi-email mode, no addresses)

Notes:
  - email_change.html tests use the test-only URL "account_email_change_test"
    (registered in tests/urls.py) because EmailView.template_name is class-level.
  - Users with email="" are used for "no email" states so allauth's
    sync_user_email_address() does not auto-create EmailAddress records.
  - verified_email_required.html is captured without authentication because the
    test-only URL registered in tests/urls.py does not require login.
"""

import pytest
from allauth.account.models import EmailAddress
from django.urls import reverse

from screenshots.conftest import create_test_user

# ---------------------------------------------------------------------------
# Browser login helper
# ---------------------------------------------------------------------------


def _browser_login(page, live_server, username, password="testpass123"):
    """Log in through the allauth login form and wait for the redirect."""
    response = page.goto(live_server.url + reverse("account_login"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500, (
        f"Login page returned HTTP {response.status}"
    )
    page.fill("input[name=login]", username)
    page.fill("input[name=password]", password)
    with page.expect_navigation(wait_until="networkidle"):
        page.click("button[type=submit]")


# ---------------------------------------------------------------------------
# US1 / email_change.html states
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_email_change_no_pending(
    page, live_server, settings, django_user_model, save_screenshot
):
    """Screenshot: email_change.html — 1 verified email, no pending change."""
    settings.ACCOUNT_CHANGE_EMAIL = True
    user = create_test_user(django_user_model)
    EmailAddress.objects.create(
        user=user, email=user.email, verified=True, primary=True
    )

    _browser_login(page, live_server, user.username)
    response = page.goto(live_server.url + reverse("account_email_change_test"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500, (
        f"Server returned HTTP {response.status} for email-change-no-pending"
    )
    save_screenshot("email-change-no-pending")


@pytest.mark.django_db(transaction=True)
def test_email_change_pending(
    page, live_server, settings, django_user_model, save_screenshot
):
    """Screenshot: email_change.html — current email + pending new address."""
    settings.ACCOUNT_CHANGE_EMAIL = True
    user = create_test_user(django_user_model)
    EmailAddress.objects.create(
        user=user, email=user.email, verified=True, primary=True
    )
    EmailAddress.objects.create(
        user=user,
        email="pending@example.com",
        verified=False,
        primary=False,
    )

    _browser_login(page, live_server, user.username)
    response = page.goto(live_server.url + reverse("account_email_change_test"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500, (
        f"Server returned HTTP {response.status} for email-change-pending"
    )
    save_screenshot("email-change-pending")


@pytest.mark.django_db(transaction=True)
def test_email_change_no_email(
    page, live_server, settings, django_user_model, save_screenshot
):
    """Screenshot: email_change.html — user with no email addresses (warn_no_email shown).

    User is created with email="" so sync_user_email_address() is a no-op.
    """
    settings.ACCOUNT_CHANGE_EMAIL = True
    # Empty email prevents sync_user_email_address from auto-creating EmailAddress
    user = django_user_model.objects.create_user(
        username="noemailuser",
        email="",
        password="testpass123",
    )

    _browser_login(page, live_server, user.username)
    response = page.goto(live_server.url + reverse("account_email_change_test"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500, (
        f"Server returned HTTP {response.status} for email-change-no-email"
    )
    save_screenshot("email-change-no-email")


# ---------------------------------------------------------------------------
# US2 / email.html states
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_email_multi_list(
    page, live_server, settings, django_user_model, save_screenshot
):
    """Screenshot: email.html — 2 addresses: 1 verified primary, 1 unverified."""
    settings.ACCOUNT_CHANGE_EMAIL = False
    user = create_test_user(django_user_model)
    EmailAddress.objects.create(
        user=user, email=user.email, verified=True, primary=True
    )
    EmailAddress.objects.create(
        user=user,
        email="second@example.com",
        verified=False,
        primary=False,
    )

    _browser_login(page, live_server, user.username)
    response = page.goto(live_server.url + reverse("account_email"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500, (
        f"Server returned HTTP {response.status} for email-multi-list"
    )
    save_screenshot("email-multi-list")


@pytest.mark.django_db(transaction=True)
def test_email_warn_no_email(
    page, live_server, settings, django_user_model, save_screenshot
):
    """Screenshot: email.html — multi-email mode, no addresses (warn_no_email shown).

    User is created with email="" so sync_user_email_address() is a no-op.
    """
    settings.ACCOUNT_CHANGE_EMAIL = False
    user = django_user_model.objects.create_user(
        username="noemailuser2",
        email="",
        password="testpass123",
    )

    _browser_login(page, live_server, user.username)
    response = page.goto(live_server.url + reverse("account_email"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500, (
        f"Server returned HTTP {response.status} for email-warn-no-email"
    )
    save_screenshot("email-warn-no-email")


# ---------------------------------------------------------------------------
# US3 / verified_email_required.html
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_email_verified_required(live_server, settings, capture_screenshot):
    """Screenshot: verified_email_required.html — gate page.

    Uses the test-only URL registered in tests/urls.py which does not require
    authentication (mirroring how allauth's decorator renders the template inline).
    """
    settings.SOCIALACCOUNT_ENABLED = False
    capture_screenshot(
        reverse("account_verified_email_required"), "email-verified-required"
    )
