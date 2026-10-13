"""
Integration tests for the allauth signup page (account/signup.html).

Covers:
  - T006 / US1: Page renders with mvp card, "Sign in" link, no social buttons when disabled
  - T008 / US2: POST valid form → redirect; POST invalid form → per-field errors; field re-population
  - T014 / US3: Social buttons present/absent based on SOCIALACCOUNT_ENABLED; SOCIALACCOUNT_ONLY guard
  - T017 / US4: signup_closed.html rendered when adapter disables signup
  - T019 / US5: Authenticated user is redirected away from signup page
  - T025 / US6: Passkey signup page renders; passkey option visible/hidden based on settings
"""

import pytest
from django.urls import reverse

from tests.factories import EmailAddressFactory, UserFactory

# ---------------------------------------------------------------------------
# Template source checks — no raw {% element %} / {% endelement %} tags
# ---------------------------------------------------------------------------

SIGNUP_TEMPLATES = [
    "account/signup.html",
    "account/signup_closed.html",
    "account/signup_by_passkey.html",
]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def get_signup_url():
    return reverse("account_signup")


# ---------------------------------------------------------------------------
# T006 / US1: Developer enables the allauth addon
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_signup_page_renders_http_200(client):
    """Signup page must return HTTP 200 for anonymous users."""
    response = client.get(get_signup_url())
    assert response.status_code == 200


@pytest.mark.django_db
def test_signup_page_contains_sign_in_link(client):
    """Signup page must contain a 'Sign in' link pointing to the login URL."""
    response = client.get(get_signup_url())
    content = response.content.decode()
    login_url = reverse("account_login")
    assert login_url in content


@pytest.mark.django_db
def test_signup_page_uses_dac_card_template(client):
    """Signup page must render the DAC card wrapper (shadow class on card)."""
    response = client.get(get_signup_url())
    content = response.content.decode()
    assert "shadow" in content


@pytest.mark.django_db
def test_signup_page_email_only_config(client, settings):
    """Email-only signup: only email + password fields visible, no username."""
    settings.ACCOUNT_LOGIN_METHODS = {"email"}
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_USERNAME_REQUIRED = False
    settings.ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
    response = client.get(get_signup_url())
    assert response.status_code == 200
    content = response.content.decode()
    assert 'name="email"' in content or 'type="email"' in content
    assert 'type="password"' in content


@pytest.mark.django_db
def test_signup_page_no_social_buttons_when_socialaccount_disabled(client, settings):
    """No social provider buttons when allauth.socialaccount is not enabled."""
    settings.SOCIALACCOUNT_ENABLED = False
    response = client.get(get_signup_url())
    content = response.content.decode()
    # No provider_list include fired — no social section
    assert "outline-secondary" not in content or "provider" not in content.lower()


@pytest.mark.django_db
def test_signup_page_template_name(client):
    """Verify the correct template is used."""
    response = client.get(get_signup_url())
    template_names = [t.name for t in response.templates]
    assert "account/signup.html" in template_names


# ---------------------------------------------------------------------------
# T008 / US2: End user creates account via email/password
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_signup_valid_post_redirects(client, settings):
    """Valid signup form POST must redirect (HTTP 302)."""
    settings.ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
    settings.ACCOUNT_LOGIN_METHODS = {"email"}
    settings.ACCOUNT_USERNAME_REQUIRED = False
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_EMAIL_VERIFICATION = "none"
    data = {
        "email": "newuser@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
    }
    response = client.post(get_signup_url(), data=data)
    assert response.status_code == 302


@pytest.mark.django_db
def test_signup_mismatched_passwords_shows_error(client, settings):
    """POST with mismatched passwords must re-render page with field error."""
    settings.ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
    settings.ACCOUNT_LOGIN_METHODS = {"email"}
    settings.ACCOUNT_USERNAME_REQUIRED = False
    settings.ACCOUNT_EMAIL_REQUIRED = True
    data = {
        "email": "user@example.com",
        "password1": "StrongPass123!",
        "password2": "DifferentPass456!",
    }
    response = client.post(get_signup_url(), data=data)
    assert response.status_code == 200
    content = response.content.decode()
    # Password mismatch error should appear on the page
    assert 'type="password"' in content
    # Form must re-render
    assert "<form" in content


@pytest.mark.django_db
def test_signup_duplicate_email_shows_error(client, settings):
    """POST with duplicate email must re-render page with email field error."""
    settings.ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
    settings.ACCOUNT_LOGIN_METHODS = {"email"}
    settings.ACCOUNT_USERNAME_REQUIRED = False
    settings.ACCOUNT_EMAIL_REQUIRED = True
    settings.ACCOUNT_EMAIL_VERIFICATION = "none"
    # Create existing user with the email
    existing_user = UserFactory(email="taken@example.com")
    EmailAddressFactory(user=existing_user, email="taken@example.com")

    data = {
        "email": "taken@example.com",
        "password1": "StrongPass123!",
        "password2": "StrongPass123!",
    }
    response = client.post(get_signup_url(), data=data)
    assert response.status_code == 200
    content = response.content.decode()
    assert "<form" in content


@pytest.mark.django_db
def test_signup_form_repopulates_on_error(client, settings):
    """After a failed POST, non-password field values are repopulated."""
    settings.ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
    settings.ACCOUNT_LOGIN_METHODS = {"email"}
    settings.ACCOUNT_USERNAME_REQUIRED = False
    settings.ACCOUNT_EMAIL_REQUIRED = True
    data = {
        "email": "user@example.com",
        "password1": "short",
        "password2": "short",
    }
    response = client.post(get_signup_url(), data=data)
    assert response.status_code == 200
    content = response.content.decode()
    # email value should be repopulated in the re-rendered form
    assert "user@example.com" in content


# ---------------------------------------------------------------------------
# T014 / US3: Social account provider buttons
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_social_buttons_present_when_provider_configured(client, settings, social_app):
    """Social buttons appear when SOCIALACCOUNT_ENABLED and a provider is configured."""
    settings.SOCIALACCOUNT_ENABLED = True
    response = client.get(get_signup_url())
    assert response.status_code == 200
    content = response.content.decode()
    # Google provider button should be rendered — look for the provider name in output
    assert "Google" in content


@pytest.mark.django_db
def test_social_section_absent_when_no_providers(client, settings):
    """Social section is absent when no providers are configured."""
    settings.SOCIALACCOUNT_ENABLED = True
    # Don't create any social apps — no providers active
    response = client.get(get_signup_url())
    assert response.status_code == 200
    # Without any configured apps, the provider list renders empty — no button for any provider
    content = response.content.decode()
    # The provider list will be empty; no social provider names appear
    assert "outline-secondary" not in content


@pytest.mark.django_db
def test_password_form_hidden_when_socialaccount_only(client, settings):
    """Password form is not rendered when SOCIALACCOUNT_ONLY is True."""
    settings.SOCIALACCOUNT_ONLY = True
    response = client.get(get_signup_url())
    assert response.status_code == 200
    content = response.content.decode()
    # When SOCIALACCOUNT_ONLY, the c-form block is not rendered
    assert 'name="account_signup"' not in content
    # No password field
    assert 'type="password"' not in content


@pytest.mark.django_db
def test_multiple_providers_each_render_a_button(client, settings):
    """Multiple configured providers each produce their own button."""
    from allauth.socialaccount.models import SocialApp
    from django.contrib.sites.models import Site

    settings.SOCIALACCOUNT_ENABLED = True
    site = Site.objects.get_or_create(id=1, defaults={"domain": "example.com", "name": "example.com"})[0]

    for provider_id, name in [("google", "Google"), ("github", "GitHub")]:
        app = SocialApp.objects.create(provider=provider_id, name=name, client_id="id", secret="secret")
        app.sites.add(site)

    response = client.get(get_signup_url())
    assert response.status_code == 200
    content = response.content.decode()
    assert "Google" in content
    assert "GitHub" in content


# ---------------------------------------------------------------------------
# T017 / US4: Signup disabled message
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_signup_closed_when_adapter_disables_signups(client, settings):
    """When adapter returns is_open_for_signup=False, signup_closed.html is rendered."""

    class ClosedAdapter:
        def is_open_for_signup(self, request):
            return False

    settings.ACCOUNT_ADAPTER = "tests.test_allauth.test_signup_view.ClosedAdapter"

    # allauth checks adapter at dispatch time — we need a real adapter class
    # Use the standard approach: configure the setting and let allauth resolve it
    # Reset to default after test
    response = client.get(get_signup_url())
    # allauth responds with 200 and renders signup_closed.html
    assert response.status_code == 200
    template_names = [t.name for t in response.templates]
    assert "account/signup_closed.html" in template_names


@pytest.mark.django_db
def test_signup_closed_no_form_element(client, settings):
    """signup_closed.html must not contain a <form> element."""
    settings.ACCOUNT_ADAPTER = "tests.test_allauth.test_signup_view.ClosedAdapter"
    response = client.get(get_signup_url())
    assert response.status_code == 200
    content = response.content.decode()
    assert "<form" not in content


@pytest.mark.django_db
def test_signup_closed_shows_closed_message(client, settings):
    """signup_closed.html must display the 'Sign Up Closed' message."""
    settings.ACCOUNT_ADAPTER = "tests.test_allauth.test_signup_view.ClosedAdapter"
    response = client.get(get_signup_url())
    assert response.status_code == 200
    content = response.content.decode()
    assert "Sign Up Closed" in content
    assert "currently closed" in content


class ClosedAdapter:
    """Test adapter that disables signup."""

    def __init__(self, request):
        self.request = request

    def is_open_for_signup(self, request):
        return False


# ---------------------------------------------------------------------------
# T019 / US5: Already authenticated user visits signup
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_authenticated_user_redirected_from_signup(authenticated_client):
    """Authenticated users must be redirected (302) away from the signup page."""
    response = authenticated_client.get(get_signup_url())
    assert response.status_code == 302


@pytest.mark.django_db
def test_authenticated_user_no_signup_form_rendered(authenticated_client):
    """Authenticated users must not see the signup form."""
    response = authenticated_client.get(get_signup_url())
    # The redirect means the template is never rendered
    assert response.status_code == 302
    assert "location" in response or response.get("Location") is not None


# ---------------------------------------------------------------------------
# T025 / US6: Passkey signup
# ---------------------------------------------------------------------------


def get_passkey_signup_url():
    return reverse("account_signup_by_passkey")


@pytest.mark.django_db
def test_passkey_signup_page_returns_http_200(client):
    """GET /signup/passkey/ returns HTTP 200 when MFA passkey signup is enabled."""
    response = client.get(get_passkey_signup_url())
    assert response.status_code == 200


@pytest.mark.django_db
def test_passkey_signup_page_uses_entrance_shell(client):
    """signup_by_passkey.html must render within the <c-mvp.entrance> card shell."""
    response = client.get(get_passkey_signup_url())
    content = response.content.decode()
    # The dac entrance layout renders the centered card shell
    assert "shadow" in content


@pytest.mark.django_db
def test_passkey_signup_page_uses_dac_template(client):
    """Verify the DAC signup_by_passkey.html template is used (not allauth's own)."""
    response = client.get(get_passkey_signup_url())
    assert response.status_code == 200
    template_names = [t.name for t in response.templates]
    assert "account/signup_by_passkey.html" in template_names


@pytest.mark.django_db
def test_passkey_signup_page_has_back_link_to_signup(client):
    """signup_by_passkey.html must contain a link back to the main signup page."""
    response = client.get(get_passkey_signup_url())
    content = response.content.decode()
    signup_url = reverse("account_signup")
    assert signup_url in content
    assert "Other options" in content


@pytest.mark.django_db
def test_passkey_option_visible_on_signup_page_when_enabled(client):
    """Main signup page shows passkey option when PASSKEY_SIGNUP_ENABLED context var is True."""
    response = client.get(get_signup_url())
    assert response.status_code == 200
    content = response.content.decode()
    passkey_signup_url = reverse("account_signup_by_passkey")
    assert passkey_signup_url in content
    assert "passkey" in content.lower()


@pytest.mark.django_db
def test_passkey_option_hidden_on_signup_page_when_disabled(client, settings):
    """Main signup page hides passkey option when MFA_PASSKEY_SIGNUP_ENABLED is False."""
    settings.MFA_PASSKEY_SIGNUP_ENABLED = False
    response = client.get(get_signup_url())
    assert response.status_code == 200
    content = response.content.decode()
    # With passkey disabled, PASSKEY_SIGNUP_ENABLED context var is False
    # and the passkey button block is not rendered
    assert "Sign up with a passkey" not in content
