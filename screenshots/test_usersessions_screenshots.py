"""
Playwright screenshot tests for the allauth user sessions management flow.

Covers T008 / Principles VIII and XIII: Multi-Viewport Screenshot Coverage.

2 page states × 2 viewports = 4 PNG files written to docs/_static/{tier}/.

Page states:
  - sessions-multiple : sessions list with ≥2 active sessions (current + others visible)
  - sessions-single   : sessions list with 1 active session (current only, "Sign Out" button)

Viewports:
  - desktop : 1440×900
  - mobile  : 390×844
"""

from pathlib import Path

import pytest
from allauth.usersessions.models import UserSession
from django.test import Client
from django.urls import reverse

from screenshots.conftest import create_test_user

REPO_ROOT = Path(__file__).resolve().parents[1]
SCREENSHOT_ROOT = REPO_ROOT / "docs" / "_static"

VIEWPORTS_2 = [
    ("desktop", 1440, 900),
    ("mobile", 390, 844),
]


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _save_screenshot_2vp(page, slug):
    """Save screenshots for desktop and mobile only (2 viewports)."""
    for tier, width, height in VIEWPORTS_2:
        page.set_viewport_size({"width": width, "height": height})
        output_dir = SCREENSHOT_ROOT / tier
        output_dir.mkdir(parents=True, exist_ok=True)
        screenshot_path = output_dir / f"{slug}.png"
        page.screenshot(path=str(screenshot_path), full_page=True)
        assert screenshot_path.exists(), (
            f"Screenshot was not written to {screenshot_path}"
        )
        assert screenshot_path.stat().st_size > 0, (
            f"Screenshot at {screenshot_path} is empty"
        )


def _browser_login(page, live_server, username, password="defaultpass123"):
    """Log in through the allauth login form and wait for the redirect."""
    response = page.goto(live_server.url + reverse("account_login"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500, (
        f"Login page returned HTTP {response.status}"
    )
    page.fill("input[name=login]", username)
    page.fill("input[name=password]", password)
    with page.expect_navigation(wait_until="networkidle"):
        page.click("button[type=submit]")


# ---------------------------------------------------------------------------
# State 1: sessions-multiple — ≥2 active sessions
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_sessions_multiple(page, live_server, django_user_model):
    """Screenshot: sessions list with multiple active sessions."""
    user = create_test_user(django_user_model)

    # Create an extra UserSession backed by a real Django session so purge_and_list keeps it
    c = Client()
    c.force_login(user)
    UserSession.objects.create(
        user=user,
        session_key=c.session.session_key,
        ip="9.9.9.9",
        user_agent="OtherBrowser/1.0 (Test Device)",
    )

    _browser_login(page, live_server, user.username, password="testpass123")
    response = page.goto(live_server.url + reverse("usersessions_list"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500, (
        f"Server returned HTTP {response.status} for sessions-multiple"
    )

    _save_screenshot_2vp(page, "sessions-multiple")


# ---------------------------------------------------------------------------
# State 2: sessions-single — 1 active session
# ---------------------------------------------------------------------------


@pytest.mark.django_db(transaction=True)
def test_sessions_single(page, live_server, django_user_model):
    """Screenshot: sessions list with only 1 active session (the current one).

    No extra UserSession records are created before login, so the browser session
    established by _browser_login is the only active session — triggering the
    'Sign Out' (single-session) branch of the template.
    """
    user = create_test_user(django_user_model)

    # Log in without pre-creating additional sessions → session_count == 1
    _browser_login(page, live_server, user.username, password="testpass123")

    response = page.goto(live_server.url + reverse("usersessions_list"))
    page.wait_for_load_state("networkidle")
    assert response is not None and response.status < 500, (
        f"Server returned HTTP {response.status} for sessions-single"
    )

    _save_screenshot_2vp(page, "sessions-single")
