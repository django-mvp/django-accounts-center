"""
Playwright screenshot tests for the allauth password reset flow.

Covers FR-013 / Principle XIII: Multi-Viewport Screenshot Coverage.

5 page states × 2 viewports = 10 PNG files written to docs/_static/{tier}/.

Page states:
  - password-reset                   : account/password_reset.html (anonymous)
  - password-reset-done              : account/password_reset_done.html
  - password-reset-from-key          : account/password_reset_from_key.html (valid token)
  - password-reset-from-key-invalid  : account/password_reset_from_key.html (token_fail=True)
  - password-reset-from-key-done     : account/password_reset_from_key_done.html

Agent visual verification (Principle XIII, NON-NEGOTIABLE):
  After TVAL-2 runs this test suite, the implementing agent MUST open and inspect
  every generated docs/_static/{desktop,mobile}/password-reset-*.png file
  before marking T008 complete.
"""

import pytest
from allauth.account.forms import default_token_generator
from allauth.account.utils import user_pk_to_url_str
from django.urls import reverse

from screenshots.conftest import create_test_user


@pytest.mark.django_db(transaction=True)
def test_password_reset_page(live_server, settings, capture_screenshot):
    """Screenshot: password_reset.html (anonymous, no social providers)."""
    settings.ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = False
    settings.SOCIALACCOUNT_ENABLED = False
    capture_screenshot(reverse("account_reset_password"), "password-reset")


@pytest.mark.django_db(transaction=True)
def test_password_reset_done_page(live_server, settings, capture_screenshot):
    """Screenshot: password_reset_done.html."""
    settings.ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = False
    capture_screenshot(reverse("account_reset_password_done"), "password-reset-done")


@pytest.mark.django_db(transaction=True)
def test_password_reset_from_key_page(
    page, live_server, settings, django_user_model, save_screenshot
):
    """Screenshot: password_reset_from_key.html (valid token — renders change-password form)."""
    settings.ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = False
    user = create_test_user(django_user_model)
    uid = user_pk_to_url_str(user)
    key = default_token_generator.make_token(user)
    url = reverse(
        "account_reset_password_from_key",
        kwargs={"uidb36": uid, "key": key},
    )
    response = page.goto(live_server.url + url)
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500, (
        f"Server returned HTTP {response.status} for reset key URL"
    )
    save_screenshot("password-reset-from-key")


@pytest.mark.django_db(transaction=True)
def test_password_reset_from_key_invalid_page(
    live_server, settings, capture_screenshot
):
    """Screenshot: password_reset_from_key.html with invalid token (token_fail branch)."""
    settings.ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = False
    url = reverse(
        "account_reset_password_from_key",
        kwargs={"uidb36": "invalid", "key": "invalid-token"},
    )
    capture_screenshot(url, "password-reset-from-key-invalid")


@pytest.mark.django_db(transaction=True)
def test_password_reset_from_key_done_page(live_server, settings, capture_screenshot):
    """Screenshot: password_reset_from_key_done.html."""
    settings.ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED = False
    capture_screenshot(
        reverse("account_reset_password_from_key_done"), "password-reset-from-key-done"
    )
