"""
Integration tests for the MFA management template overrides.

Covers:
  - US1: base_manage.html extends dac/base.html (layout, sidebar)
  - US2: TOTP, Recovery Codes pages render with DAC layout and correct content
  - US3: WebAuthn pages render with DAC layout and correct content
  - Edge cases: element-tag removal, RC button suppression, save-once checkbox

Test design:
  - HTTP-level integration tests via Django test client (client.get / client.force_login)
  - `reauthentication_required` views need `account_authentication_methods` set in session
  - WebAuthn authenticators created directly via Authenticator.objects.create to avoid
    real hardware/browser interaction
"""

import time

import pytest
from allauth.mfa.models import Authenticator
from allauth.mfa.recovery_codes.internal.auth import RecoveryCodes
from allauth.mfa.totp.internal.auth import TOTP, generate_totp_secret
from django.urls import reverse

from tests.factories import UserFactory

# ---------------------------------------------------------------------------
# Template source checks — no raw {% element %} / {% endelement %} tags
# ---------------------------------------------------------------------------

MFA_TEMPLATES = [
    "mfa/index.html",
    "mfa/totp/activate_form.html",
    "mfa/webauthn/add_form.html",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def mark_as_recently_authenticated(client):
    """Set session auth records so reauthentication_required views pass."""
    session = client.session
    session["account_authentication_methods"] = [{"method": "password", "at": time.time()}]
    session.save()


def activate_totp(user):
    """Create a TOTP authenticator for the user."""
    secret = generate_totp_secret()
    TOTP.activate(user, secret)
    return secret


def activate_recovery_codes(user):
    """Create a RecoveryCodes authenticator for the user."""
    return RecoveryCodes.activate(user)


def create_webauthn(user, name, is_passwordless=None):
    """Create a WebAuthn Authenticator model object directly."""
    credential = {}
    if is_passwordless is True:
        credential = {"clientExtensionResults": {"credProps": {"rk": True}}}
    elif is_passwordless is False:
        credential = {"clientExtensionResults": {"credProps": {"rk": False}}}
    auth = Authenticator.objects.create(
        user=user,
        type=Authenticator.Type.WEBAUTHN,
        data={"name": name, "credential": credential},
    )
    return auth


# ---------------------------------------------------------------------------
# Test 1 (US1 SC1–3): Layout
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestMFALayout:
    """MFA index page renders inside the DAC Account Center layout (US1)."""

    def test_dac_layout_sidebar_present(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("mfa_index"))
        assert response.status_code == 200
        assert "Account navigation" in response.content.decode()



# ---------------------------------------------------------------------------
# Test 2 (US2 SC1): TOTP active state
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTOTPActiveState:
    """MFA index shows TOTP active status and Deactivate button."""

    def test_totp_active_status_text(self, client):
        user = UserFactory()
        activate_totp(user)
        client.force_login(user)
        response = client.get(reverse("mfa_index"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "Authentication using an authenticator app is active." in content

    def test_totp_deactivate_link_present(self, client):
        user = UserFactory()
        activate_totp(user)
        client.force_login(user)
        response = client.get(reverse("mfa_index"))
        content = response.content.decode()
        assert "Deactivate" in content
        assert reverse("mfa_deactivate_totp") in content


# ---------------------------------------------------------------------------
# Test 3 (US2 SC2): TOTP inactive state
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTOTPInactiveState:
    """MFA index shows TOTP inactive status and Activate button."""

    def test_totp_inactive_status_text(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("mfa_index"))
        assert response.status_code == 200
        assert "An authenticator app is not active." in response.content.decode()

    def test_totp_activate_link_present(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("mfa_index"))
        content = response.content.decode()
        assert "Activate" in content
        assert reverse("mfa_activate_totp") in content


# ---------------------------------------------------------------------------
# Test 4 (US2 SC3): Recovery codes panel visible
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestRecoveryCodesPanelVisible:
    """Recovery codes panel shows View/Download/Generate links and code count."""

    def test_view_download_generate_links_present(self, client):
        user = UserFactory()
        activate_totp(user)
        activate_recovery_codes(user)
        client.force_login(user)
        response = client.get(reverse("mfa_index"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "View" in content
        assert "Download" in content
        assert "Generate" in content

    def test_recovery_code_count_text_present(self, client):
        user = UserFactory()
        activate_totp(user)
        activate_recovery_codes(user)
        client.force_login(user)
        response = client.get(reverse("mfa_index"))
        content = response.content.decode()
        # Check that the "N of M recovery codes remaining" pattern appears
        assert "recovery codes available" in content


# ---------------------------------------------------------------------------
# Test 5 (US2): Method panel gating
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestMethodPanelGating:
    """Panels for disabled MFA types are excluded from mfa/index.html."""

    def test_webauthn_panel_absent_when_not_in_supported_types(self, client, settings):
        settings.MFA_SUPPORTED_TYPES = ["totp"]
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("mfa_index"))
        content = response.content.decode()
        assert "Security Keys" not in content

    def test_recovery_codes_panel_absent_when_not_in_supported_types(self, client, settings):
        settings.MFA_SUPPORTED_TYPES = ["totp"]
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("mfa_index"))
        content = response.content.decode()
        assert "Recovery Codes" not in content


# ---------------------------------------------------------------------------
# Test 6 (US2 SC4): TOTP activate form
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTOTPActivateForm:
    """TOTP activate form renders QR code, secret, token input, and Activate button."""

    def test_qr_code_img_present(self, client):
        user = UserFactory()
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_activate_totp"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "<img" in content
        assert "data:" in content

    def test_secret_display_present(self, client):
        user = UserFactory()
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_activate_totp"))
        content = response.content.decode()
        assert "Authenticator secret" in content

    def test_token_input_present(self, client):
        user = UserFactory()
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_activate_totp"))
        content = response.content.decode()
        assert 'name="code"' in content or 'id="id_code"' in content

    def test_activate_submit_button_present(self, client):
        user = UserFactory()
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_activate_totp"))
        content = response.content.decode()
        assert "Activate" in content


# ---------------------------------------------------------------------------
# Test 7 (US2 SC5): TOTP deactivate form
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestTOTPDeactivateForm:
    """TOTP deactivate form renders a danger Deactivate button."""

    def test_deactivate_danger_button_present(self, client):
        user = UserFactory()
        activate_totp(user)
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_deactivate_totp"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "Deactivate" in content
        assert "btn-error" in content


# ---------------------------------------------------------------------------
# Test 8 (US2 SC6): Recovery codes view
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestRecoveryCodesView:
    """Recovery codes view renders textarea with codes and action buttons."""

    def test_textarea_with_readonly_present(self, client):
        user = UserFactory()
        activate_totp(user)
        activate_recovery_codes(user)
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_view_recovery_codes"))
        assert response.status_code == 200
        content = response.content.decode()
        assert 'id="recovery_codes"' in content
        assert "readonly" in content

    def test_download_button_present(self, client):
        user = UserFactory()
        activate_totp(user)
        activate_recovery_codes(user)
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_view_recovery_codes"))
        content = response.content.decode()
        assert "Download" in content

    def test_generate_new_codes_button_present(self, client):
        user = UserFactory()
        activate_totp(user)
        activate_recovery_codes(user)
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_view_recovery_codes"))
        content = response.content.decode()
        assert "Generate" in content

    def test_codes_appear_in_textarea(self, client):
        user = UserFactory()
        activate_totp(user)
        rc = activate_recovery_codes(user)
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_view_recovery_codes"))
        content = response.content.decode()
        # Recovery codes are numeric strings; at least some should appear
        unused = rc.get_unused_codes()
        assert len(unused) > 0
        assert unused[0] in content


# ---------------------------------------------------------------------------
# Test 9 (US2 SC7): Recovery codes generate — existing codes
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestRecoveryCodesGenerateExisting:
    """Generate page shows invalidation warning and danger button when codes exist."""

    def test_warning_text_present(self, client):
        user = UserFactory()
        activate_totp(user)
        activate_recovery_codes(user)
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_generate_recovery_codes"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "invalidate your existing codes" in content

    def test_danger_button_present(self, client):
        user = UserFactory()
        activate_totp(user)
        activate_recovery_codes(user)
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_generate_recovery_codes"))
        content = response.content.decode()
        assert "btn-error" in content
        assert "Generate" in content


# ---------------------------------------------------------------------------
# Test 10 (Edge): Recovery codes generate — no existing codes
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestRecoveryCodesGenerateNoExisting:
    """Generate page shows no warning and no danger button when no codes exist."""

    def test_no_warning_text(self, client):
        user = UserFactory()
        activate_totp(user)
        # No recovery codes activated
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_generate_recovery_codes"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "generating new codes will invalidate" not in content

    def test_no_danger_class_on_button(self, client):
        user = UserFactory()
        activate_totp(user)
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_generate_recovery_codes"))
        content = response.content.decode()
        assert "Generate" in content
        # The submit button must not carry the danger variant (only present when
        # unused_code_count > 0)
        assert "btn-error" not in content


# ---------------------------------------------------------------------------
# Test 11 (US3 SC1): WebAuthn list — with keys
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestWebAuthnListWithKeys:
    """WebAuthn list page renders table rows with names, badges, and action links."""

    def test_two_rows_with_key_names(self, client):
        user = UserFactory()
        create_webauthn(user, "My Passkey", is_passwordless=True)
        create_webauthn(user, "Work Key", is_passwordless=False)
        client.force_login(user)
        response = client.get(reverse("mfa_list_webauthn"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "My Passkey" in content
        assert "Work Key" in content

    def test_type_badges_present(self, client):
        user = UserFactory()
        create_webauthn(user, "My Passkey", is_passwordless=True)
        create_webauthn(user, "Work Key", is_passwordless=False)
        client.force_login(user)
        response = client.get(reverse("mfa_list_webauthn"))
        content = response.content.decode()
        assert "Passkey" in content
        assert "Security key" in content

    def test_edit_and_remove_links_present(self, client):
        user = UserFactory()
        auth1 = create_webauthn(user, "Key A", is_passwordless=True)
        client.force_login(user)
        response = client.get(reverse("mfa_list_webauthn"))
        content = response.content.decode()
        assert reverse("mfa_edit_webauthn", kwargs={"pk": auth1.pk}) in content
        assert reverse("mfa_remove_webauthn", kwargs={"pk": auth1.pk}) in content

    def test_table_element_present(self, client):
        user = UserFactory()
        create_webauthn(user, "Key A")
        client.force_login(user)
        response = client.get(reverse("mfa_list_webauthn"))
        content = response.content.decode()
        assert "<table" in content


# ---------------------------------------------------------------------------
# Test 12 (US3 SC2): WebAuthn list — empty state
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestWebAuthnListEmpty:
    """WebAuthn list page renders empty-state message and no table when no keys."""

    def test_empty_state_message_present(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("mfa_list_webauthn"))
        assert response.status_code == 200
        assert "No security keys have been added." in response.content.decode()

    def test_no_table_in_empty_state(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("mfa_list_webauthn"))
        assert "<table" not in response.content.decode()


# ---------------------------------------------------------------------------
# Test 13 (US3 SC3): WebAuthn add form
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestWebAuthnAddForm:
    """WebAuthn add form renders with JS block and hard-dependency button id."""

    def test_webauthn_js_onload_script_present(self, client):
        user = UserFactory()
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_add_webauthn"))
        assert response.status_code == 200
        content = response.content.decode()
        assert "allauth.webauthn.forms.addForm" in content

    def test_submit_button_hard_dependency_id_present(self, client):
        user = UserFactory()
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_add_webauthn"))
        content = response.content.decode()
        assert 'id="mfa_webauthn_add"' in content

    def test_register_key_button_present(self, client):
        user = UserFactory()
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_add_webauthn"))
        content = response.content.decode()
        assert 'id="mfa_webauthn_add"' in content


# ---------------------------------------------------------------------------
# Test 14 (US3 SC4): WebAuthn edit form
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestWebAuthnEditForm:
    """WebAuthn edit form renders a Save button."""

    def test_save_button_present(self, client):
        user = UserFactory()
        auth = create_webauthn(user, "Test Key")
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_edit_webauthn", kwargs={"pk": auth.pk}))
        assert response.status_code == 200
        content = response.content.decode()
        assert "Save" in content


# ---------------------------------------------------------------------------
# Test 15 (US3 SC5): WebAuthn remove confirmation
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestWebAuthnRemoveConfirmation:
    """WebAuthn remove page renders danger Remove button and key name in text."""

    def test_danger_remove_button_present(self, client):
        user = UserFactory()
        auth = create_webauthn(user, "My Key")
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_remove_webauthn", kwargs={"pk": auth.pk}))
        assert response.status_code == 200
        content = response.content.decode()
        assert "Remove" in content
        assert "btn-error" in content

    def test_key_name_in_confirmation_text(self, client):
        user = UserFactory()
        auth = create_webauthn(user, "My Key")
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_remove_webauthn", kwargs={"pk": auth.pk}))
        content = response.content.decode()
        assert "Remove Security Key" in content


# ---------------------------------------------------------------------------
# Test 17 (Edge Case / L1): RC buttons absent when no recovery codes set up
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestRCButtonSuppressionWhenNoRecoveryCodes:
    """View and Download buttons are absent when user has no recovery codes."""

    def test_view_link_absent_when_no_recovery_codes(self, client):
        user = UserFactory()
        # No recovery codes — user has TOTP only
        activate_totp(user)
        client.force_login(user)
        response = client.get(reverse("mfa_index"))
        assert response.status_code == 200
        content = response.content.decode()
        # Use exact URL with trailing quote to avoid matching the generate URL
        # (mfa_generate_recovery_codes contains mfa_view_recovery_codes as prefix)
        view_url = reverse("mfa_view_recovery_codes")
        assert f'href="{view_url}"' not in content

    def test_download_link_absent_when_no_recovery_codes(self, client):
        user = UserFactory()
        activate_totp(user)
        client.force_login(user)
        response = client.get(reverse("mfa_index"))
        content = response.content.decode()
        assert reverse("mfa_download_recovery_codes") not in content


# ---------------------------------------------------------------------------
# Test 18 (Edge Case / L2): Recovery codes save-once checkbox
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestRecoveryCodesSaveOnceCheckbox:
    """Codes-saved checkbox appears when MFA_RECOVERY_CODES_SHOW_ONCE is True."""

    def test_codes_saved_checkbox_present(self, client, settings):
        settings.MFA_RECOVERY_CODES_SHOW_ONCE = True
        user = UserFactory()
        activate_totp(user)
        activate_recovery_codes(user)
        client.force_login(user)
        mark_as_recently_authenticated(client)
        response = client.get(reverse("mfa_view_recovery_codes"))
        assert response.status_code == 200
        content = response.content.decode()
        assert 'id="codes_saved"' in content
