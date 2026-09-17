"""
Playwright screenshot tests for the allauth social account connections flow.

Covers T013–T015 / Principles VIII and XIII: Multi-Viewport Screenshot Coverage.

3 page states × 2 viewports = 6 PNG files written to docs/_static/{tier}/.

Page states:
  - connections-has-accounts   : connections.html — user with 1 Google social account
  - connections-no-accounts    : connections.html — authenticated user with no social accounts
  - authentication-error       : authentication_error.html — third-party login error page

Viewports:
  - desktop : 1440×900
  - mobile  : 390×844

Agent visual verification (Principle XIII, NON-NEGOTIABLE):
  After running this test suite the implementing agent MUST open and inspect
  every generated docs/_static/{desktop,mobile}/connections-*.png and
  authentication-error.png before marking T015 complete.
"""

import pytest
from allauth.socialaccount.models import SocialAccount
from django.urls import reverse

from screenshots.conftest import create_google_social_app, create_test_user

# ---------------------------------------------------------------------------
# Helpers
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


def _create_google_social_account(user):
    """Create a Google SocialAccount for the given user (requires SocialApp to exist first)."""
    return SocialAccount.objects.create(
        user=user,
        provider="google",
        uid=f"google-uid-{user.pk}",
        extra_data={"name": user.username, "email": user.email},
    )


# ---------------------------------------------------------------------------
# State 1: connections-has-accounts
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_connections_has_accounts(
    page, live_server, settings, django_user_model, save_screenshot
):
    """Screenshot: connections.html — authenticated user with 1 Google account connected."""
    user = create_test_user(django_user_model)
    create_google_social_app()
    _create_google_social_account(user)

    _browser_login(page, live_server, user.username)
    response = page.goto(live_server.url + reverse("socialaccount_connections"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500, (
        f"Server returned HTTP {response.status} for connections-has-accounts"
    )
    save_screenshot("connections-has-accounts")


# ---------------------------------------------------------------------------
# State 2: connections-no-accounts
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_connections_no_accounts(
    page, live_server, settings, django_user_model, save_screenshot
):
    """Screenshot: connections.html — authenticated user with no social accounts (empty state)."""
    user = create_test_user(django_user_model)

    _browser_login(page, live_server, user.username)
    response = page.goto(live_server.url + reverse("socialaccount_connections"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500, (
        f"Server returned HTTP {response.status} for connections-no-accounts"
    )
    save_screenshot("connections-no-accounts")


# ---------------------------------------------------------------------------
# State 3: authentication-error
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_authentication_error(live_server, capture_screenshot):
    """Screenshot: authentication_error.html — third-party login failure page.

    The view always returns HTTP 401; capture_screenshot checks status < 500
    so 401 is accepted.
    """
    capture_screenshot(reverse("socialaccount_login_error"), "authentication-error")
