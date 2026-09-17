"""
Playwright screenshot tests for the allauth email verification flow.

Covers FR-007 / Principle XIII: Multi-Viewport Screenshot Coverage.

5 page states × 2 viewports = 10 PNG files written to docs/_static/{tier}/.

Page states:
  - email-verification-sent      : account/verification_sent.html (anonymous)
  - email-confirm-valid          : account/email_confirm.html (can_confirm=True)
  - email-confirm-invalid        : account/email_confirm.html (invalid/expired key)
  - email-verification-code      : account/confirm_email_verification_code.html
  - account-inactive             : account/account_inactive.html

Agent visual verification (Principle XIII, NON-NEGOTIABLE):
  After TVAL-3 runs this test suite, the implementing agent MUST open and inspect
  every generated docs/_static/{desktop,mobile}/email-*.png and
  account-inactive.png file before marking T011 complete.
"""

import pytest
from allauth.account.models import EmailAddress, EmailConfirmation
from django.urls import reverse

from screenshots.conftest import create_test_user


@pytest.mark.django_db(transaction=True)
def test_email_verification_sent_page(live_server, settings, capture_screenshot):
    """Screenshot: verification_sent.html (anonymous, no social providers)."""
    settings.SOCIALACCOUNT_ENABLED = False
    settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = False
    capture_screenshot(
        reverse("account_email_verification_sent"), "email-verification-sent"
    )


@pytest.mark.django_db(transaction=True)
def test_email_confirm_valid_page(
    page, live_server, settings, django_user_model, save_screenshot
):
    """Screenshot: email_confirm.html with a valid confirmation key (can_confirm=True branch)."""
    settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = False
    # Disable HMAC so the view uses DB-backed EmailConfirmation.from_key().
    # HMAC keys contain colons which crash Django's static file handler on Windows.
    settings.ACCOUNT_EMAIL_CONFIRMATION_HMAC = False
    user = create_test_user(django_user_model)
    email_address = EmailAddress.objects.create(
        user=user,
        email=user.email,
        verified=False,
        primary=True,
    )
    confirmation = EmailConfirmation.create(email_address)
    key = confirmation.key
    url = reverse("account_confirm_email", kwargs={"key": key})
    response = page.goto(live_server.url + url)
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500, (
        f"Server returned HTTP {response.status} for email confirm URL"
    )
    save_screenshot("email-confirm-valid")


@pytest.mark.django_db(transaction=True)
def test_email_confirm_invalid_page(live_server, settings, capture_screenshot):
    """Screenshot: email_confirm.html with an invalid/expired key (no-confirmation branch)."""
    settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = False
    url = reverse(
        "account_confirm_email", kwargs={"key": "invalid-key-that-will-never-match"}
    )
    capture_screenshot(url, "email-confirm-invalid")


@pytest.mark.django_db(transaction=True)
def test_email_verification_code_page(
    page, live_server, settings, django_user_model, save_screenshot
):
    """
    Screenshot: confirm_email_verification_code.html.

    The template has no dedicated URL — it is served through allauth's stage
    pipeline at account_email_verification_sent when
    ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED=True and a pending stage is in
    the session. We trigger it by creating a user with an unverified email and
    submitting the signup form so allauth sets up the pending stage, then
    visiting account_email_verification_sent which is the resumable stage URL.
    """
    settings.ACCOUNT_EMAIL_VERIFICATION = "mandatory"
    settings.ACCOUNT_EMAIL_VERIFICATION_BY_CODE_ENABLED = True
    settings.SOCIALACCOUNT_ENABLED = False

    # Sign up a new user — allauth will set up the email verification stage
    response = page.goto(live_server.url + reverse("account_signup"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500

    page.fill("input[name=username]", "codeuser")
    page.fill("input[name=email]", "codeuser@example.com")
    page.fill("input[name=password1]", "TestPass!123")
    page.fill("input[name=password2]", "TestPass!123")
    with page.expect_navigation(wait_until="networkidle"):
        page.click("button[type=submit]")

    # Now visit the verification-sent URL — with a pending stage it should render
    # confirm_email_verification_code.html (the resumable stage)
    response = page.goto(live_server.url + reverse("account_email_verification_sent"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500, (
        f"Server returned HTTP {response.status} for email verification code URL"
    )
    save_screenshot("email-verification-code")


@pytest.mark.django_db(transaction=True)
def test_account_inactive_page(live_server, settings, capture_screenshot):
    """Screenshot: account_inactive.html (deactivated-account redirect)."""
    settings.SOCIALACCOUNT_ENABLED = False
    capture_screenshot(reverse("account_inactive"), "account-inactive")
