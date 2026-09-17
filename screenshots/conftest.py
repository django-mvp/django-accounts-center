"""Shared pytest fixtures and helpers for Playwright screenshot tests."""

from pathlib import Path

import pytest
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]  # django-accounts-center/
SCREENSHOT_ROOT = REPO_ROOT / "docs" / "_static"

VIEWPORTS = [
    ("desktop", 1440, 900),
    ("mobile", 390, 844),
]

# ---------------------------------------------------------------------------
# Database helpers (regular functions, called conditionally inside tests)
# ---------------------------------------------------------------------------


def create_google_social_app():
    """Create a Google SocialApp associated with site 1 and return it."""
    site, _ = Site.objects.get_or_create(
        id=1, defaults={"domain": "example.com", "name": "Example"}
    )
    app = SocialApp.objects.create(
        provider="google", name="Google", client_id="test-id", secret="test-secret"
    )
    app.sites.add(site)
    return app


def create_test_user(django_user_model):
    """Create a basic user for authenticated flows."""
    return django_user_model.objects.create_user(
        username="testuser", email="test@example.com", password="testpass123"
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def save_screenshot(page):
    """
    Provide a callable that resizes to each canonical viewport in turn and
    captures a full-page screenshot of the current page state.

    Usage::

        save_screenshot(slug)

    Writes one file per viewport to ``docs/_static/{tier}/{slug}.png``.
    Fails the test if any screenshot file is missing or empty.
    """

    def _save(slug):
        for tier, width, height in VIEWPORTS:
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

    return _save


@pytest.fixture
def capture_screenshot(page, live_server, save_screenshot):
    """
    Provide a callable that navigates to a URL and captures screenshots at all
    canonical viewport sizes in a single test.

    Usage::

        capture_screenshot(url, slug)

    Fails the test if:

    - The server responds with HTTP 5xx.
    - Any screenshot file is missing or empty.
    """

    def _capture(url, slug):
        response = page.goto(live_server.url + url)
        page.wait_for_load_state("networkidle")
        assert response is not None, f"No response received for {live_server.url + url}"
        assert response.status < 500, (
            f"Server returned HTTP {response.status} for {live_server.url + url}"
        )
        save_screenshot(slug)

    return _capture
