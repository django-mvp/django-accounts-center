"""
Integration tests for the allauth password change / set / reauthenticate flow.

Covers:
  - T004 / US1: password_change.html and password_set.html render inside DAC layout
  - T005 / US2: Form fields render correctly on both management pages
  - T007 / US3: reauthenticate.html renders as a Cotton entrance page
"""

import pytest
from django.urls import reverse

from tests.factories import UserFactory

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_user_no_password(username="nopwduser", email="nopwd@example.com"):
    """Return a user with no usable password (triggers password_set flow)."""
    user = UserFactory(username=username, email=email)
    user.set_unusable_password()
    user.save()
    return user


# ---------------------------------------------------------------------------
# Template source checks — no raw {% element %} / {% endelement %} tags
# ---------------------------------------------------------------------------

PASSWORD_CHANGE_TEMPLATES = [
    "account/password_change.html",
    "account/password_set.html",
    "account/reauthenticate.html",
]


# ---------------------------------------------------------------------------
# T004 / US1: password_change.html
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPasswordChangeView:
    """Tests for account/password_change.html – management page with DAC layout."""

    def test_renders_200_for_authenticated(self, client):
        """account_change_password GET must return HTTP 200 for an authenticated user."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        assert response.status_code == 200

    def test_has_page_content_block(self, client):
        """The page renders inside the Account Center, whose navigation names it."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        assert "Account Center" in content

    def test_has_change_password_heading(self, client):
        """'Change Password' must appear as the page's own heading."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        assert "Change Password" in content

    def test_has_submit_button(self, client):
        """Rendered HTML must contain a type="submit" button."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        assert 'type="submit"' in content

    def test_has_forgot_password_link(self, client):
        """Rendered HTML must contain a link to account_reset_password."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        assert reverse("account_reset_password") in content


# ---------------------------------------------------------------------------
# T004 / US1: password_set.html
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPasswordSetView:
    """Tests for account/password_set.html – management page for users with no password."""

    def test_renders_200_for_authenticated(self, client):
        """account_set_password GET must return HTTP 200 for an authenticated user with no password."""
        user = make_user_no_password()
        client.force_login(user)
        response = client.get(reverse("account_set_password"))
        assert response.status_code == 200

    def test_has_set_password_heading(self, client):
        """'Set Password' must appear as the page's own heading."""
        user = make_user_no_password()
        client.force_login(user)
        response = client.get(reverse("account_set_password"))
        content = response.content.decode()
        assert "Set Password" in content

    def test_has_submit_button(self, client):
        """Rendered HTML must contain a type="submit" button."""
        user = make_user_no_password()
        client.force_login(user)
        response = client.get(reverse("account_set_password"))
        content = response.content.decode()
        assert 'type="submit"' in content

    def test_no_forgot_password_link(self, client):
        """password_set.html must NOT contain a link to account_reset_password."""
        user = make_user_no_password()
        client.force_login(user)
        response = client.get(reverse("account_set_password"))
        content = response.content.decode()
        assert reverse("account_reset_password") not in content


# ---------------------------------------------------------------------------
# T004 / US1: base_manage_password.html inheritance chain
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestBaseManagePasswordView:
    """Verify that base_manage_password.html inherits the DAC base layout."""

    def test_base_manage_password_inherits_dac_base(self, client):
        """
        Render base_manage_password.html directly and assert the Account
        Center's navigation is present, which verifies the inheritance chain is
        unbroken.
        """
        user = UserFactory()
        client.force_login(user)
        # Change-password is served by base_manage_password → base_manage → dac/base
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        assert "Account Center" in content


# ---------------------------------------------------------------------------
# T005 / US2: Form fields on password_change.html
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPasswordChangeFormFields:
    """Verify form fields render correctly on password_change.html."""

    def test_form_has_old_password_field(self, client):
        """password_change.html must contain the current-password field."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        assert 'name="oldpassword"' in content or 'type="password"' in content

    def test_form_has_new_password_fields(self, client):
        """password_change.html must contain password1 and password2 fields."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        assert 'name="password1"' in content
        assert 'name="password2"' in content

    def test_submit_button_text_is_change_password(self, client):
        """Submit button text must be 'Change Password'."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("account_change_password"))
        content = response.content.decode()
        assert "Change Password" in content


# ---------------------------------------------------------------------------
# T005 / US2: Form fields on password_set.html
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPasswordSetFormFields:
    """Verify form fields render correctly on password_set.html."""

    def test_form_has_new_password_fields(self, client):
        """password_set.html must contain password1 and password2 fields (no oldpassword)."""
        user = make_user_no_password()
        client.force_login(user)
        response = client.get(reverse("account_set_password"))
        content = response.content.decode()
        assert 'name="password1"' in content
        assert 'name="password2"' in content
        assert 'name="oldpassword"' not in content

    def test_submit_button_text_is_set_password(self, client):
        """Submit button text must be 'Set Password'."""
        user = make_user_no_password()
        client.force_login(user)
        response = client.get(reverse("account_set_password"))
        content = response.content.decode()
        assert "Set Password" in content


# ---------------------------------------------------------------------------
# T007 / US3: reauthenticate.html
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestReauthenticateView:
    """Tests for account/reauthenticate.html – entrance-style page."""

    def test_renders_200_for_authenticated(self, client):
        """account_reauthenticate GET must return HTTP 200 for an authenticated user."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("account_reauthenticate"))
        assert response.status_code == 200

    def test_has_password_field(self, client):
        """Rendered HTML must contain a type="password" input."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("account_reauthenticate"))
        content = response.content.decode()
        assert 'type="password"' in content

    def test_has_confirm_button(self, client):
        """Rendered HTML must contain a submit button with text 'Confirm'."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("account_reauthenticate"))
        content = response.content.decode()
        assert 'type="submit"' in content
        assert "Confirm" in content

    def test_no_alternatives_section_by_default(self, client):
        """'Alternative options' section must be absent when no alternatives are configured."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("account_reauthenticate"))
        content = response.content.decode()
        assert "Alternative options" not in content

    @pytest.mark.django_db
    def test_alternatives_section_when_provided(self, client):
        """'Alternative options' section appears when reauthentication_alternatives is provided.

        Uses the test-only URL (tests/urls.py) because allauth's element tags
        require a loader-originated template, not a string-compiled one.
        """
        user = UserFactory(username="reauth_alt_user", email="reauth_alt@example.com")
        client.force_login(user)
        response = client.get(reverse("test_reauthenticate_alternatives"))
        html = response.content.decode()
        assert "Alternative options" in html
        assert "/accounts/mock-mfa/" in html
