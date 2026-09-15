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


# The widths mvp's <c-entrance> expresses, each as the class it puts on the
# card (see the `size` c-var in django-mvp's cotton/entrance/index.html).
# "full" is the absence of all of them: the card fills its container.
_SCALE = ("sm", "md", "lg", "xl", "2xl", "3xl", "4xl")
_DEFAULT_WIDTH_CLASS = "md:max-w-2xl"


def _width_classes(card):
    """Every width class on the rendered card. One, or none for "full"."""
    return [name for name in card.get("class", []) if name.startswith("md:max-w-")]


class TestEntranceComponentWidth:
    def test_default_renders_todays_width(self, cotton_render_string_soup):
        """A layout that overrides nothing keeps the width these pages have
        always rendered at, so adopting the scale changes no existing page."""
        soup = cotton_render_string_soup(_ENTRANCE + "{% block content %}Hi{% endblock content %}")
        card = soup.find("div", class_="card")
        assert card is not None
        assert _width_classes(card) == [_DEFAULT_WIDTH_CLASS]

    @pytest.mark.parametrize("size", _SCALE)
    def test_each_declared_width_reaches_the_card(self, size, cotton_render_string_soup):
        """A page declaring any width in mvp's scale gets that width, and only
        that one — the whole point of #20."""
        soup = cotton_render_string_soup(_entrance_with_size(size))
        card = soup.find("div", class_="card")
        assert card is not None
        assert _width_classes(card) == [f"md:max-w-{size}"]
        # Declaring a width must not cost the page its content: {% block content %}
        # moves inside the {% block entrance %} override, and still has to arrive.
        assert soup.find(id="mine") is not None

    def test_size_full_renders_an_unconstrained_card(self, cotton_render_string_soup):
        """"full" carries no width class at all, so the card fills its
        container."""
        soup = cotton_render_string_soup(_entrance_with_size("full"))
        card = soup.find("div", class_="card")
        assert card is not None
        assert _width_classes(card) == []
        assert soup.find(id="mine") is not None

    def test_declared_widths_render_distinct_cards(self, cotton_render_string_soup):
        """Two pages declaring different widths differ on the card itself."""
        cards = []
        for size in ("md", "4xl", "full"):
            soup = cotton_render_string_soup(_entrance_with_size(size))
            cards.append(tuple(_width_classes(soup.find("div", class_="card"))))
        assert len(set(cards)) == len(cards)

    def test_unrecognised_size_falls_back_to_default_width(self, cotton_render_string_soup):
        """A width outside mvp's scale falls back to the default rather than
        reaching the markup: django-mvp's stylesheet carries only the widths
        its own component names, so an invented class would style nothing."""
        soup = cotton_render_string_soup(_entrance_with_size("huge"))
        card = soup.find("div", class_="card")
        assert card is not None
        assert _width_classes(card) == [_DEFAULT_WIDTH_CLASS]
        assert "md:max-w-huge" not in card.get("class", [])
