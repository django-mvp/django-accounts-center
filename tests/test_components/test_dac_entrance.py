"""
Cotton rendering tests for the shared entrance page (dac/entrance.html) and
its <c-dac.entrance> component (cotton/dac/entrance.html).

The entrance page is the core package's extension point for anonymous-facing
pages: any integration reaches it with a bare {% extends %} and fills
{% block content %}, and gets the full-screen background, the centered card,
the site logo, the package stylesheet and the messages region for free —
without depending on, or referencing, any integration template.
"""

from types import SimpleNamespace

import pytest

# Bare-minimum child template: extends the core entrance page, no block
# overrides. This belongs to no app, which is the point (SC-001).
_ENTRANCE = '{% extends "dac/entrance.html" %}{% load i18n %}'


class TestEntrancePageBlockContract:
    def test_full_screen_background_present(self, cotton_render_string_soup):
        """mvp's <c-entrance> background wraps the page (full-screen, centered)."""
        soup = cotton_render_string_soup(_ENTRANCE)
        background = soup.find("div", class_="min-h-screen")
        assert background is not None

    def test_one_centered_card_present(self, cotton_render_string_soup):
        """Exactly one card renders (mvp's <c-entrance> card) — no app supplies
        its own card markup."""
        soup = cotton_render_string_soup(_ENTRANCE)
        cards = soup.find_all("div", class_="card")
        assert len(cards) == 1

    def test_site_logo_present(self, cotton_render_string_soup):
        """The site logo renders above the content, inside the card."""
        soup = cotton_render_string_soup(_ENTRANCE)
        img = soup.find("img", alt="Site Logo")
        assert img is not None

    def test_content_block_override_renders(self, cotton_render_string_soup):
        """{% block content %} content reaches the DOM inside the card."""
        template = _ENTRANCE + '{% block content %}<p id="my-content">Hello</p>{% endblock content %}'
        soup = cotton_render_string_soup(template)
        el = soup.find(id="my-content")
        assert el is not None
        assert el.get_text(strip=True) == "Hello"

    def test_stylesheet_link_present(self, cotton_render_string_soup):
        """The entrance page carries a stylesheet, so an extending page never
        has to know about one (FR-009).

        It is django-mvp's, reached by leaving the styles block alone. This
        package ships none of its own, and overriding that block by mistake is
        how a page would end up with no stylesheet at all."""
        soup = cotton_render_string_soup(_ENTRANCE)
        hrefs = [link.get("href") or "" for link in soup.find_all("link", rel="stylesheet")]
        assert any("django-mvp.css" in href for href in hrefs)
        assert not any("dac.css" in href for href in hrefs)

    def test_messages_region_present(self, cotton_render_string_soup):
        """mvp's <c-messages> toast region renders even with no messages
        queued (FR-011)."""
        soup = cotton_render_string_soup(_ENTRANCE)
        toast = soup.find("div", class_="toast")
        assert toast is not None

    def test_queued_message_displays(self, cotton_render_string_soup):
        """A queued message reaches the page, so an extending page inherits a
        working messages region rather than an empty container (FR-011)."""
        message = SimpleNamespace(level_tag="error", tags="error", message="Wrong password.")
        soup = cotton_render_string_soup(_ENTRANCE, {"messages": [message]})
        toast = soup.find("div", class_="toast")
        assert toast is not None
        assert "Wrong password." in toast.get_text()


class TestEntranceStandsAloneWithoutAnIntegration:
    """The whole point of moving the page into the core package: it must render
    with no integration installed (SC-004). The architecture guardrail checks
    the templates name no integration; this renders one with dac.allauth taken
    out of INSTALLED_APPS, which is the claim itself."""

    @pytest.fixture
    def without_allauth_integration(self, settings):
        settings.INSTALLED_APPS = [app for app in settings.INSTALLED_APPS if app != "dac.allauth"]
        return settings

    def test_page_renders_without_the_allauth_integration(self, without_allauth_integration, cotton_render_string_soup):
        template = _ENTRANCE + '{% block content %}<p id="mine">Mine</p>{% endblock content %}'
        soup = cotton_render_string_soup(template)
        assert soup.find("div", class_="min-h-screen") is not None
        assert soup.find("div", class_="card") is not None
        assert soup.find("img", alt="Site Logo") is not None
        assert soup.find(id="mine") is not None


class TestEntranceComponentConsistency:
    def test_two_distinct_pages_share_structure(self, cotton_render_string_soup):
        """Two unrelated pages extending the entrance page get identical chrome."""
        template_a = _ENTRANCE + "{% block content %}Page A{% endblock content %}"
        template_b = _ENTRANCE + "{% block content %}Page B{% endblock content %}"
        for template in (template_a, template_b):
            soup = cotton_render_string_soup(template)
            assert soup.find("div", class_="min-h-screen") is not None
            assert soup.find("img", alt="Site Logo") is not None


def _entrance_with_size(size):
    """A layout declaring a card width, written exactly as the README documents
    it: {% block entrance %} is overridden and {% block content %} is nested
    inside that override. A page cannot also declare content at the top level —
    Django rejects the same block name twice in one template."""
    return (
        '{% extends "dac/entrance.html" %}{% load i18n %}'
        "{% block entrance %}"
        f'<c-dac.entrance size="{size}">'
        '{% block content %}<p id="mine">Hi</p>{% endblock content %}'
        "</c-dac.entrance>"
        "{% endblock entrance %}"
    )


# mvp's <c-entrance small> branch adds this class (see the `small` c-var in
# django-mvp's cotton/entrance/index.html); its absence is the "full" branch.
_SMALL_WIDTH_CLASS = "md:max-w-2xl"


class TestEntranceComponentWidth:
    def test_default_renders_todays_width(self, cotton_render_string_soup):
        """A layout that overrides nothing keeps today's (small) card width."""
        soup = cotton_render_string_soup(_ENTRANCE + "{% block content %}Hi{% endblock content %}")
        card = soup.find("div", class_="card")
        assert card is not None
        assert _SMALL_WIDTH_CLASS in card.get("class", [])

    def test_size_full_renders_wider_card(self, cotton_render_string_soup):
        """A layout overriding {% block entrance %} with size="full" drops
        mvp's small-width class, rendering a wider card than the default."""
        template = _entrance_with_size("full")
        soup = cotton_render_string_soup(template)
        card = soup.find("div", class_="card")
        assert card is not None
        assert _SMALL_WIDTH_CLASS not in card.get("class", [])
        # Declaring a width must not cost the page its content: {% block content %}
        # moves inside the {% block entrance %} override, and still has to arrive.
        assert soup.find(id="mine") is not None

    def test_default_and_full_card_classes_differ(self, cotton_render_string_soup):
        """The default and size="full" branches render distinct card classes."""
        default_soup = cotton_render_string_soup(_ENTRANCE + "{% block content %}Hi{% endblock content %}")
        full_template = _entrance_with_size("full")
        full_soup = cotton_render_string_soup(full_template)

        default_card = default_soup.find("div", class_="card")
        full_card = full_soup.find("div", class_="card")
        assert default_card.get("class", []) != full_card.get("class", [])

    def test_unrecognised_size_falls_back_to_default_width(self, cotton_render_string_soup):
        """An unrecognised size value falls back to today's width rather than
        emitting broken markup."""
        template = _entrance_with_size("huge")
        soup = cotton_render_string_soup(template)
        card = soup.find("div", class_="card")
        assert card is not None
        assert _SMALL_WIDTH_CLASS in card.get("class", [])
