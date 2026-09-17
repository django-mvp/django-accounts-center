"""
Playwright screenshot tests for the allauth signup page.

Covers FR-011 / Principle XIII: Multi-Viewport Screenshot Coverage.

Each test function covers one visually distinct settings permutation and
captures screenshots at all three canonical viewport sizes in a single run.

Viewports (captured by the capture_screenshot fixture):
  - desktop  : 1440×900
  - mobile   : 390×844

Agent visual verification (Principle XIII, NON-NEGOTIABLE):
  After TVAL-5 runs this test suite, the implementing agent MUST open and inspect
  every generated docs/_static/{desktop,mobile}/signup-page-*.png file
  and signup-by-passkey-page-*.png before marking TVAL-5 complete.
"""

import pytest
from django.urls import reverse

from screenshots.conftest import create_google_social_app


@pytest.mark.django_db(transaction=True)
def test_signup_page_social_disabled(live_server, settings, capture_screenshot):
    settings.SOCIALACCOUNT_ENABLED = False
    capture_screenshot(reverse("account_signup"), "signup-page-social-disabled")


@pytest.mark.django_db(transaction=True)
def test_signup_page_social_enabled(live_server, settings, capture_screenshot):
    settings.SOCIALACCOUNT_ENABLED = True
    settings.SOCIALACCOUNT_ONLY = False
    create_google_social_app()
    capture_screenshot(reverse("account_signup"), "signup-page-social-enabled")


@pytest.mark.django_db(transaction=True)
def test_signup_page_social_only(live_server, settings, capture_screenshot):
    settings.SOCIALACCOUNT_ENABLED = True
    settings.SOCIALACCOUNT_ONLY = True
    settings.MFA_PASSKEY_SIGNUP_ENABLED = (
        False  # Avoid passkey UI elements interfering with social-only test
    )
    create_google_social_app()
    capture_screenshot(reverse("account_signup"), "signup-page-social-only")


@pytest.mark.django_db(transaction=True)
def test_signup_page_signup_closed(live_server, settings, capture_screenshot):
    settings.ACCOUNT_ADAPTER = "tests.test_allauth.adapters.ClosedSignupAdapter"
    capture_screenshot(reverse("account_signup"), "signup-page-signup-closed")


@pytest.mark.django_db(transaction=True)
def test_signup_page_passkey_enabled(live_server, settings, capture_screenshot):
    settings.MFA_PASSKEY_SIGNUP_ENABLED = True
    settings.SOCIALACCOUNT_ENABLED = False
    capture_screenshot(reverse("account_signup"), "signup-page-passkey-enabled")


@pytest.mark.django_db(transaction=True)
def test_signup_by_passkey_page(live_server, settings, capture_screenshot):
    settings.MFA_PASSKEY_SIGNUP_ENABLED = True
    settings.SOCIALACCOUNT_ENABLED = False
    capture_screenshot(reverse("account_signup_by_passkey"), "signup-by-passkey-page")
