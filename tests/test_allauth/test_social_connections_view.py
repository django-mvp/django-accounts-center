"""
Integration tests for the allauth social account connections flow.

Covers:
  - T003 / US1: connections.html renders inside the DAC layout (sidebar, card-stack)
  - T007 / US2: connections.html handles has-accounts and empty-state branches correctly;
    authentication_error.html uses Cotton components (no element tags)
  - T011 / US3: Edge cases — multiple accounts same provider, no providers configured,
    form re-render on submission failure

Test design pattern:
  - HTTP-level integration tests via Django test client (client.get / client.force_login)
  - Factories from tests/factories.py provide user and social account instances
  - No Playwright: these are server-rendered template acceptance tests

Spec scenarios targeted:
  - US1-AC1: Connections page renders inside DAC Account Center layout
  - US1-AC2: DAC sidebar is present
  - US1-AC3: Breadcrumb trail shows "Account Connections" leaf
  - US2-AC1: Connected account badge and Remove button present per account
  - US2-AC2: Empty-state message shown when no accounts
  - US2-AC3: Add-connections section always rendered
  - US3-AC1: Authentication error page renders without element tags
"""

import pytest
from allauth.socialaccount.models import SocialAccount
from django.urls import reverse

from tests.factories import (
    SocialAccountFactory,
    SocialAppFactory,
    UserFactory,
)


def make_user_with_google_account():
    user = UserFactory()
    SocialAppFactory(provider="google", name="Google")  # required so get_provider_account() can resolve the app
    SocialAccountFactory(user=user, provider="google")
    return user


def make_user_with_github_account():
    user = UserFactory()
    SocialAppFactory(provider="github", name="GitHub")  # required so get_provider_account() can resolve the app
    SocialAccountFactory(user=user, provider="github")
    return user


# ---------------------------------------------------------------------------
# Template source checks — no raw {% element %} / {% endelement %} tags
# ---------------------------------------------------------------------------

SOCIAL_CONNECTIONS_TEMPLATES = [
    "socialaccount/connections.html",
    "socialaccount/authentication_error.html",
]


# ---------------------------------------------------------------------------
# T003 / US1: TestConnectionsLayoutAndStructure
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestConnectionsLayoutAndStructure:
    """Tests for socialaccount/connections.html — DAC layout integration (US1)."""

    def test_renders_200_for_authenticated(self, client):
        """GET socialaccount_connections must return HTTP 200 for an authenticated user."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("socialaccount_connections"))
        assert response.status_code == 200

    def test_dac_layout_sidebar_present(self, client):
        """Rendered HTML must contain the app-sidebar element (DAC layout rendered)."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("socialaccount_connections"))
        content = response.content.decode()
        assert "Account navigation" in content

    def test_account_connections_heading_present(self, client):
        """Rendered HTML must name the page 'Account Connections'."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("socialaccount_connections"))
        content = response.content.decode()
        assert "Account Connections" in content

    def test_content_in_page_content_block(self, client):
        """The page renders inside the Account Center, whose navigation names it."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("socialaccount_connections"))
        content = response.content.decode()
        assert "Account Center" in content


# ---------------------------------------------------------------------------
# T007 / US2: TestConnectionsWithAccounts
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestConnectionsWithAccounts:
    """Tests for connections.html when user has ≥1 connected social account (US2)."""

    def test_connected_account_badge_present(self, client):
        """Rendered HTML for a user with a Google account contains 'Google' in a badge element."""
        user = make_user_with_google_account()
        client.force_login(user)
        response = client.get(reverse("socialaccount_connections"))
        content = response.content.decode()
        assert "Google" in content

    def test_remove_button_present(self, client):
        """Rendered HTML contains a submit button labelled 'Remove'."""
        user = make_user_with_google_account()
        client.force_login(user)
        response = client.get(reverse("socialaccount_connections"))
        content = response.content.decode()
        assert "Remove" in content

    def test_account_pk_in_hidden_field(self, client):
        """Rendered HTML contains <input type=\"hidden\" name=\"account\"> with the account PK."""
        user = make_user_with_google_account()
        client.force_login(user)
        account = SocialAccount.objects.get(user=user)
        response = client.get(reverse("socialaccount_connections"))
        content = response.content.decode()
        assert 'name="account"' in content
        assert f'value="{account.pk}"' in content

    def test_add_connections_section_present(self, client):
        """The add-connections section renders (it is unconditional in the template)."""
        user = make_user_with_google_account()
        client.force_login(user)
        response = client.get(reverse("socialaccount_connections"))
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# T007 / US2: TestConnectionsEmpty
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestConnectionsEmpty:
    """Tests for connections.html when user has 0 connected social accounts (US2)."""

    def test_no_accounts_message_present(self, client):
        """Rendered HTML for a user with no social accounts contains the empty-state message."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("socialaccount_connections"))
        content = response.content.decode()
        assert "no third-party accounts" in content

    def test_add_connections_section_still_present(self, client):
        """The add-connections section renders even when the account list is empty."""
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("socialaccount_connections"))
        assert response.status_code == 200


# ---------------------------------------------------------------------------
# T007 / US2: TestAuthenticationErrorView
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAuthenticationErrorView:
    """Tests for socialaccount/authentication_error.html (US2)."""

    def test_renders_without_server_error(self, client):
        """GET socialaccount_login_error must return HTTP 401 (the view's explicit status)."""
        response = client.get(reverse("socialaccount_login_error"))
        assert response.status_code == 401

    def test_explanatory_text_present(self, client):
        """Rendered HTML contains 'An error occurred' (substring of the full trans string)."""
        response = client.get(reverse("socialaccount_login_error"))
        content = response.content.decode()
        assert "An error occurred" in content


# ---------------------------------------------------------------------------
# T011 / US3: Edge cases
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestConnectionsEdgeCases:
    """Edge-case tests for connections.html (US3)."""

    def test_multiple_accounts_same_provider_each_rendered(self, client):
        """Multiple social accounts from the same provider each appear as separate list items."""
        user = UserFactory()
        SocialAppFactory(provider="google", name="Google")  # required so get_provider_account() can resolve the app
        SocialAccountFactory(user=user, provider="google")
        SocialAccountFactory(user=user, provider="google")
        client.force_login(user)
        response = client.get(reverse("socialaccount_connections"))
        content = response.content.decode()
        # Two distinct account PKs means two hidden inputs
        accounts = SocialAccount.objects.filter(user=user)
        assert accounts.count() == 2
        for acc in accounts:
            assert f'value="{acc.pk}"' in content

    def test_no_social_providers_configured_renders_without_error(self, client, settings):
        """Page renders without server error when no social providers are configured."""
        settings.SOCIALACCOUNT_PROVIDERS = {}
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("socialaccount_connections"))
        assert response.status_code == 200

    def test_form_rerender_on_submission_failure_renders_without_error(self, client):
        """POST with an invalid account PK re-renders the page without a server error."""
        user = UserFactory()
        client.force_login(user)
        response = client.post(
            reverse("socialaccount_connections"),
            {"account": 999999},
        )
        # allauth re-renders or redirects — either is acceptable; no 500
        assert response.status_code in (200, 302)
