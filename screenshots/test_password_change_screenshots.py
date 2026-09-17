"""
Playwright screenshot tests for the allauth password change / set / reauthenticate pages.

Covers FR-011 / Principle XIII: Multi-Viewport Screenshot Coverage.

4 page states × 2 viewports = 8 PNGs saved to docs/_static/{desktop,mobile}/.

Viewports:
  - desktop  : 1440×900
  - mobile   : 390×844
"""

import pytest
from django.urls import reverse

from screenshots.conftest import create_test_user

# ---------------------------------------------------------------------------
# Helper: log in via the Django test client session and transfer to Playwright
# ---------------------------------------------------------------------------


def _login_and_get_session_cookie(live_server, client, user):
    """
    Force-login via the Django test client so we can transfer the session
    cookie to the Playwright page for authenticated screenshots.
    """
    client.force_login(user)
    session_cookie = client.cookies.get("sessionid")
    return session_cookie.value if session_cookie else None


# ---------------------------------------------------------------------------
# Password Change page (management — requires authenticated user)
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_password_change_page(
    page, live_server, client, django_user_model, save_screenshot
):
    """Authenticated user sees password_change.html in the Account Center layout."""
    user = create_test_user(django_user_model)

    # Transfer session to Playwright
    client.force_login(user)
    session_value = client.cookies["sessionid"].value
    page.goto(live_server.url + "/")
    page.context.add_cookies(
        [{"name": "sessionid", "value": session_value, "url": live_server.url}]
    )

    response = page.goto(live_server.url + reverse("account_change_password"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500
    save_screenshot("password-change")


# ---------------------------------------------------------------------------
# Password Set page (management — requires user with no usable password)
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_password_set_page(
    page, live_server, client, django_user_model, save_screenshot
):
    """Authenticated user with no password sees password_set.html with DAC layout."""
    user = django_user_model.objects.create_user(
        username="nopwduser", email="nopwd@example.com", password="temp"
    )
    user.set_unusable_password()
    user.save()

    client.force_login(user)
    session_value = client.cookies["sessionid"].value
    page.goto(live_server.url + "/")
    page.context.add_cookies(
        [{"name": "sessionid", "value": session_value, "url": live_server.url}]
    )

    response = page.goto(live_server.url + reverse("account_set_password"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500
    save_screenshot("password-set")


# ---------------------------------------------------------------------------
# Reauthenticate page (entrance layout — requires authenticated user)
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_reauthenticate_page(
    page, live_server, client, django_user_model, save_screenshot
):
    """Authenticated user sees reauthenticate.html as an entrance-style page."""
    user = create_test_user(django_user_model)

    client.force_login(user)
    session_value = client.cookies["sessionid"].value
    page.goto(live_server.url + "/")
    page.context.add_cookies(
        [{"name": "sessionid", "value": session_value, "url": live_server.url}]
    )

    response = page.goto(live_server.url + reverse("account_reauthenticate"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500
    save_screenshot("reauthenticate")


# ---------------------------------------------------------------------------
# Reauthenticate with alternatives (test-only URL)
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_reauthenticate_with_alternatives_page(
    page, live_server, client, django_user_model, save_screenshot
):
    """Reauthenticate page with mock reauthentication_alternatives shows 'Alternative options'."""
    user = create_test_user(django_user_model)

    client.force_login(user)
    session_value = client.cookies["sessionid"].value
    page.goto(live_server.url + "/")
    page.context.add_cookies(
        [{"name": "sessionid", "value": session_value, "url": live_server.url}]
    )

    response = page.goto(live_server.url + reverse("test_reauthenticate_alternatives"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500
    save_screenshot("reauthenticate-alternatives")
