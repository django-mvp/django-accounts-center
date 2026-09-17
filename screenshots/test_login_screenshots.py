"""
Playwright screenshot tests for the allauth login page.

Covers FR-011 / Principle XIII: Multi-Viewport Screenshot Coverage.

Each test function covers one visually distinct settings permutation and
captures screenshots at all three canonical viewport sizes in a single run.

Viewports (captured by the save_screenshot / capture_screenshot fixtures):
  - desktop  : 1440×900
  - mobile   : 390×844

Agent visual verification (Principle XIII, NON-NEGOTIABLE):
  After TVAL-3 runs this test suite, the implementing agent MUST open and inspect
  every generated docs/_static/{desktop,mobile}/login-*.png file
  before marking T011 complete.
"""

import pytest
from django.urls import reverse

from screenshots.conftest import create_google_social_app, create_test_user

# ---------------------------------------------------------------------------
# Login page permutations
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_login_page_social_disabled(live_server, settings, capture_screenshot):
    settings.SOCIALACCOUNT_ENABLED = False
    settings.ACCOUNT_LOGIN_BY_CODE_ENABLED = True
    capture_screenshot(reverse("account_login"), "login-page-social-disabled")


@pytest.mark.django_db(transaction=True)
def test_login_page_social_enabled(live_server, settings, capture_screenshot):
    settings.SOCIALACCOUNT_ENABLED = True
    settings.SOCIALACCOUNT_ONLY = False
    settings.ACCOUNT_LOGIN_BY_CODE_ENABLED = True
    create_google_social_app()
    capture_screenshot(reverse("account_login"), "login-page-social-enabled")


@pytest.mark.django_db(transaction=True)
def test_login_page_social_only(live_server, settings, capture_screenshot):
    settings.SOCIALACCOUNT_ENABLED = True
    settings.SOCIALACCOUNT_ONLY = True
    create_google_social_app()
    capture_screenshot(reverse("account_login"), "login-page-social-only")


@pytest.mark.django_db(transaction=True)
def test_login_page_login_by_code(live_server, settings, capture_screenshot):
    settings.SOCIALACCOUNT_ENABLED = False
    settings.ACCOUNT_LOGIN_BY_CODE_ENABLED = True
    settings.MFA_PASSKEY_LOGIN_ENABLED = False
    capture_screenshot(reverse("account_login"), "login-page-login-by-code")


@pytest.mark.django_db(transaction=True)
def test_login_page_passkey_enabled(live_server, settings, capture_screenshot):
    settings.SOCIALACCOUNT_ENABLED = False
    settings.ACCOUNT_LOGIN_BY_CODE_ENABLED = True
    settings.MFA_PASSKEY_LOGIN_ENABLED = True
    capture_screenshot(reverse("account_login"), "login-page-passkey-enabled")


@pytest.mark.django_db(transaction=True)
def test_login_request_code_page(live_server, settings, capture_screenshot):
    settings.ACCOUNT_LOGIN_BY_CODE_ENABLED = True
    capture_screenshot(reverse("account_request_login_code"), "login-request-code-page")


@pytest.mark.django_db(transaction=True)
def test_login_confirm_code_page(
    page, live_server, settings, django_user_model, save_screenshot
):
    """Reach the confirm-code page by submitting the request-code form, then screenshot."""
    settings.ACCOUNT_LOGIN_BY_CODE_ENABLED = True
    user = create_test_user(django_user_model)
    response = page.goto(live_server.url + reverse("account_request_login_code"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500, (
        f"Server returned HTTP {response.status} for account_request_login_code"
    )
    page.fill("input[type=email]", user.email)
    with page.expect_navigation() as nav_info:
        page.click("button[type=submit]")
    page.wait_for_load_state("networkidle")
    nav_response = nav_info.value
    if nav_response is not None:
        assert nav_response.status < 500, (
            f"Server returned HTTP {nav_response.status} during login code submission"
        )
    save_screenshot("login-confirm-code-page")


# ---------------------------------------------------------------------------
# Social account permutations
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_socialaccount_login_confirm(live_server, settings, capture_screenshot):
    """GET to provider login URL shows login.html when SOCIALACCOUNT_LOGIN_ON_GET=False."""
    settings.SOCIALACCOUNT_ENABLED = True
    settings.SOCIALACCOUNT_LOGIN_ON_GET = False
    create_google_social_app()
    capture_screenshot(
        reverse("google_login") + "?process=login", "socialaccount-login-confirm"
    )


@pytest.mark.django_db(transaction=True)
def test_socialaccount_login_cancelled(live_server, capture_screenshot):
    capture_screenshot(
        reverse("socialaccount_login_cancelled"), "socialaccount-login-cancelled"
    )
