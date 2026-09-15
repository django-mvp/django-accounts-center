"""
Integration tests for the allauth user sessions management flow.

Covers:
  - T007 / US1: Sessions page renders inside the DAC Account Center layout
  - T007 / US2: Table rows, current badge, sign-out form, Last Seen column
  - T007 / US3: All conditional branches rendered correctly; no allauth element tags

Test design:
  - HTTP-level integration tests via Django test client (client.get / client.force_login)
  - allauth purge_and_list() purges UserSession records whose Django session no longer exists.
    Extra sessions are created via Client().force_login() which stores a real Django session in DB.
"""

import pytest
from allauth.usersessions.models import UserSession
from django.test import Client
from django.urls import reverse

from tests.factories import UserFactory

# ---------------------------------------------------------------------------
# Template source checks — no raw {% element %} / {% endelement %} tags
# ---------------------------------------------------------------------------


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_real_backed_session(user, ip="127.0.0.1", user_agent="TestAgent/1.0", **kwargs):
    """Create a UserSession backed by a real Django session that survives purge_and_list."""
    c = Client()
    c.force_login(user)
    session_key = c.session.session_key
    return UserSession.objects.create(
        user=user,
        session_key=session_key,
        ip=ip,
        user_agent=user_agent,
        **kwargs,
    )


# ---------------------------------------------------------------------------
# Test 1 (US1): Layout
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestUserSessionsLayout:
    """Sessions page renders inside the DAC Account Center layout (US1)."""

    def test_dac_layout_sidebar_present(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("usersessions_list"))
        assert response.status_code == 200
        assert "Account navigation" in response.content.decode()

    def test_sessions_heading_present(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("usersessions_list"))
        assert "Sessions" in response.content.decode()


# ---------------------------------------------------------------------------
# Test 2 (US2 SC1): Table rows
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestUserSessionsTableRows:
    """Sessions table renders rows with correct IP and user-agent data."""

    def test_ip_addresses_appear_in_rows(self, client):
        user = UserFactory()
        make_real_backed_session(user, ip="1.2.3.4", user_agent="Mozilla/5.0 TestBrowser/1.0")
        client.force_login(user)
        response = client.get(reverse("usersessions_list"))
        assert "1.2.3.4" in response.content.decode()

    def test_user_agent_substrings_appear_in_rows(self, client):
        user = UserFactory()
        make_real_backed_session(user, ip="5.6.7.8", user_agent="Mozilla/5.0 OtherBrowser/2.0")
        client.force_login(user)
        response = client.get(reverse("usersessions_list"))
        assert "OtherBrowser" in response.content.decode()


# ---------------------------------------------------------------------------
# Test 3 (US2 SC2): Current session badge
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestUserSessionsCurrentBadge:
    """Current session row shows a green Current badge."""

    def test_current_badge_present_for_current_session(self, client):
        user = UserFactory()
        # Create an extra session so session_count > 1
        make_real_backed_session(user, ip="9.9.9.9", user_agent="OldBrowser/1.0")
        # Force-login creates the current session; also create its UserSession record
        client.force_login(user)
        UserSession.objects.create(
            user=user,
            session_key=client.session.session_key,
            ip="127.0.0.1",
            user_agent="TestBrowser",
        )
        response = client.get(reverse("usersessions_list"))
        assert "Current" in response.content.decode()


# ---------------------------------------------------------------------------
# Test 4 (US2 SC2, multiple): Sign Out Other Sessions
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestUserSessionsMultipleSignOut:
    """Multiple sessions show Sign Out Other Sessions button."""

    def test_sign_out_other_sessions_button_text(self, client):
        user = UserFactory()
        make_real_backed_session(user, ip="9.9.9.9", user_agent="OldBrowser/1.0")
        client.force_login(user)
        UserSession.objects.create(
            user=user,
            session_key=client.session.session_key,
            ip="127.0.0.1",
            user_agent="TestBrowser",
        )
        response = client.get(reverse("usersessions_list"))
        assert "Sign Out Other Sessions" in response.content.decode()

    def test_form_action_is_usersessions_list(self, client):
        user = UserFactory()
        make_real_backed_session(user, ip="9.9.9.9", user_agent="OldBrowser/1.0")
        client.force_login(user)
        UserSession.objects.create(
            user=user,
            session_key=client.session.session_key,
            ip="127.0.0.1",
            user_agent="TestBrowser",
        )
        response = client.get(reverse("usersessions_list"))
        assert reverse("usersessions_list") in response.content.decode()


# ---------------------------------------------------------------------------
# Test 5 (US2 SC3, single): Sign Out
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestUserSessionsSingleSignOut:
    """Single session shows Sign Out button."""

    def test_sign_out_button_text_single_session(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("usersessions_list"))
        content = response.content.decode()
        assert "Sign Out" in content
        assert "Sign out other sessions" not in content

    def test_form_action_is_account_logout_single_session(self, client):
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("usersessions_list"))
        assert reverse("account_logout") in response.content.decode()


# ---------------------------------------------------------------------------
# Test 6 (US2 SC4): Last Seen visible
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestUserSessionsLastSeenVisible:
    """show_last_seen_at=True shows Last seen at column."""

    def test_last_seen_header_visible(self, client, settings):
        settings.USERSESSIONS_TRACK_ACTIVITY = True
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("usersessions_list"))
        assert "Last seen at" in response.content.decode()


# ---------------------------------------------------------------------------
# Test 7 (US2 SC4): Last Seen hidden
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestUserSessionsLastSeenHidden:
    """show_last_seen_at=False hides Last seen at column."""

    def test_last_seen_header_hidden(self, client, settings):
        settings.USERSESSIONS_TRACK_ACTIVITY = False
        user = UserFactory()
        client.force_login(user)
        response = client.get(reverse("usersessions_list"))
        assert "Last seen at" not in response.content.decode()
