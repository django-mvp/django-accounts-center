"""
Playwright screenshot tests for the MFA management flow.

Covers T018 / Principles VIII and XIII: Multi-Viewport Screenshot Coverage.

11 page states × 2 viewports = 22 PNG files written to docs/_static/{tier}/.

Page states:
  - mfa-overview-active        : MFA index with TOTP + recovery codes active
  - mfa-overview-inactive      : MFA index with no authenticators
  - mfa-totp-activate          : TOTP activation form
  - mfa-totp-deactivate        : TOTP deactivation confirmation form
  - mfa-recovery-codes-view    : Recovery codes view (textarea with codes)
  - mfa-recovery-codes-generate: Generate new recovery codes form (with warning)
  - mfa-webauthn-list          : WebAuthn list with one key
  - mfa-webauthn-list-empty    : WebAuthn list with no keys
  - mfa-webauthn-add           : WebAuthn add key form
  - mfa-webauthn-edit          : WebAuthn edit key form
  - mfa-webauthn-remove        : WebAuthn remove key confirmation

Viewports:
  - desktop : 1440×900
  - mobile  : 390×844
"""

from pathlib import Path

import pytest
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
from allauth.mfa.totp.internal.auth import TOTP, generate_totp_secret
from django.urls import reverse

from screenshots.conftest import create_test_user

REPO_ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_ROOT = REPO_ROOT / "docs" / "_static"

VIEWPORTS_2 = [
    ("desktop", 1440, 900),
    ("mobile", 390, 844),
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _save_screenshot_2vp(page, slug):
    """Save screenshots at desktop and mobile viewports."""
    for tier, width, height in VIEWPORTS_2:
        page.set_viewport_size({"width": width, "height": height})
        output_dir = SCREENSHOT_ROOT / tier
        output_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = output_dir / f"{slug}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        assert screenshot_path.exists(), f"Screenshot not written: {screenshot_path}"
        assert screenshot_path.stat().st_size > 0, (
            f"Screenshot empty: {screenshot_path}"
        )


def _browser_login(page, live_server, username, password="testpass123"):
    """Log in via the allauth login form and wait for redirect."""
    page.goto(live_server.url + reverse("account_login"))
    page.wait_for_load_state("networkidle")
    page.fill("input[name=login]", username)
    page.fill("input[name=password]", password)
    with page.expect_navigation(wait_until="networkidle"):
        page.click("button[type=submit]")


def _goto(page, live_server, url_name, **kwargs):
    """Navigate to a named URL and wait for the page to settle."""
    response = page.goto(live_server.url + reverse(url_name, **kwargs))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500, (
        f"Server returned HTTP {response.status} for {url_name}"
    )


# ---------------------------------------------------------------------------
# State 1: mfa-overview-active — index with TOTP + RC active
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_mfa_overview_active(page, live_server, django_user_model):
    """Screenshot: MFA overview with TOTP and recovery codes active."""
    user = create_test_user(django_user_model)

    # Login BEFORE activating MFA so login doesn't trigger MFA challenge.
    _browser_login(page, live_server, user.username)
    secret = generate_totp_secret()
    TOTP.activate(user, secret)
    RecoveryCodes.activate(user)

    _goto(page, live_server, "mfa_index")
    _save_screenshot_2vp(page, "mfa-overview-active")


# ---------------------------------------------------------------------------
# State 2: mfa-overview-inactive — index with no authenticators
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_mfa_overview_inactive(page, live_server, django_user_model):
    """Screenshot: MFA overview with no authenticators active."""
    user = create_test_user(django_user_model)

    _browser_login(page, live_server, user.username)
    _goto(page, live_server, "mfa_index")
    _save_screenshot_2vp(page, "mfa-overview-inactive")


# ---------------------------------------------------------------------------
# State 3: mfa-totp-activate — TOTP activation form
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_mfa_totp_activate(page, live_server, django_user_model):
    """Screenshot: TOTP activation form."""
    user = create_test_user(django_user_model)

    _browser_login(page, live_server, user.username)
    _goto(page, live_server, "mfa_activate_totp")
    _save_screenshot_2vp(page, "mfa-totp-activate")


# ---------------------------------------------------------------------------
# State 4: mfa-totp-deactivate — TOTP deactivation form
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_mfa_totp_deactivate(page, live_server, django_user_model):
    """Screenshot: TOTP deactivation confirmation form."""
    user = create_test_user(django_user_model)

    # Login BEFORE activating TOTP so login doesn't trigger TOTP MFA challenge.
    _browser_login(page, live_server, user.username)
    secret = generate_totp_secret()
    TOTP.activate(user, secret)

    _goto(page, live_server, "mfa_deactivate_totp")
    _save_screenshot_2vp(page, "mfa-totp-deactivate")


# ---------------------------------------------------------------------------
# State 5: mfa-recovery-codes-view — recovery codes view
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_mfa_recovery_codes_view(page, live_server, django_user_model):
    """Screenshot: Recovery codes view page."""
    user = create_test_user(django_user_model)

    # Login BEFORE activating MFA so login doesn't trigger MFA challenge.
    _browser_login(page, live_server, user.username)
    secret = generate_totp_secret()
    TOTP.activate(user, secret)
    RecoveryCodes.activate(user)

    _goto(page, live_server, "mfa_view_recovery_codes")
    _save_screenshot_2vp(page, "mfa-recovery-codes-view")


# ---------------------------------------------------------------------------
# State 6: mfa-recovery-codes-generate — generate form with warning
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_mfa_recovery_codes_generate(page, live_server, django_user_model):
    """Screenshot: Generate recovery codes form (with existing codes warning)."""
    user = create_test_user(django_user_model)

    # Login BEFORE activating MFA so login doesn't trigger MFA challenge.
    _browser_login(page, live_server, user.username)
    secret = generate_totp_secret()
    TOTP.activate(user, secret)
    RecoveryCodes.activate(user)

    _goto(page, live_server, "mfa_generate_recovery_codes")
    _save_screenshot_2vp(page, "mfa-recovery-codes-generate")


# ---------------------------------------------------------------------------
# State 7: mfa-webauthn-list — list with one key
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_mfa_webauthn_list(page, live_server, django_user_model):
    """Screenshot: WebAuthn authenticator list with one key registered."""
    user = create_test_user(django_user_model)

    # Login BEFORE creating the WebAuthn authenticator so login doesn't trigger
    # WebAuthn MFA challenge (which would fail with fake credential data).
    _browser_login(page, live_server, user.username)
    Authenticator.objects.create(
        user=user,
        type=Authenticator.Type.WEBAUTHN,
        data={
            "name": "My Passkey",
            "credential": {"clientExtensionResults": {"credProps": {"rk": True}}},
        },
    )

    _goto(page, live_server, "mfa_list_webauthn")
    _save_screenshot_2vp(page, "mfa-webauthn-list")


# ---------------------------------------------------------------------------
# State 8: mfa-webauthn-list-empty — list with no keys
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_mfa_webauthn_list_empty(page, live_server, django_user_model):
    """Screenshot: WebAuthn authenticator list with no keys."""
    user = create_test_user(django_user_model)

    _browser_login(page, live_server, user.username)
    _goto(page, live_server, "mfa_list_webauthn")
    _save_screenshot_2vp(page, "mfa-webauthn-list-empty")


# ---------------------------------------------------------------------------
# State 9: mfa-webauthn-add — add key form
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_mfa_webauthn_add(page, live_server, django_user_model):
    """Screenshot: WebAuthn add key form."""
    user = create_test_user(django_user_model)

    _browser_login(page, live_server, user.username)
    _goto(page, live_server, "mfa_add_webauthn")
    _save_screenshot_2vp(page, "mfa-webauthn-add")


# ---------------------------------------------------------------------------
# State 10: mfa-webauthn-edit — edit key form
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_mfa_webauthn_edit(page, live_server, django_user_model):
    """Screenshot: WebAuthn edit key form."""
    user = create_test_user(django_user_model)
    # Login BEFORE creating the WebAuthn authenticator so login doesn't trigger
    # WebAuthn MFA challenge (which would fail with fake credential data).
    _browser_login(page, live_server, user.username)
    authenticator = Authenticator.objects.create(
        user=user,
        type=Authenticator.Type.WEBAUTHN,
        data={
            "name": "My Security Key",
            "credential": {"clientExtensionResults": {"credProps": {"rk": False}}},
        },
    )
    # Recent password login satisfies reauthentication requirement.
    _goto(page, live_server, "mfa_edit_webauthn", kwargs={"pk": authenticator.pk})
    _save_screenshot_2vp(page, "mfa-webauthn-edit")


# ---------------------------------------------------------------------------
# State 11: mfa-webauthn-remove — remove confirmation
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_mfa_webauthn_remove(page, live_server, django_user_model):
    """Screenshot: WebAuthn remove key confirmation page."""
    user = create_test_user(django_user_model)
    # Login BEFORE creating the WebAuthn authenticator so login doesn't trigger
    # WebAuthn MFA challenge (which would fail with fake credential data).
    _browser_login(page, live_server, user.username)
    authenticator = Authenticator.objects.create(
        user=user,
        type=Authenticator.Type.WEBAUTHN,
        data={
            "name": "My Security Key",
            "credential": {"clientExtensionResults": {"credProps": {"rk": False}}},
        },
    )
    # Recent password login satisfies reauthentication requirement.
    _goto(page, live_server, "mfa_remove_webauthn", kwargs={"pk": authenticator.pk})
    _save_screenshot_2vp(page, "mfa-webauthn-remove")
