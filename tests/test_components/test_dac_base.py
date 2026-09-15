"""
Cotton rendering tests for dac/base.html and the sidebar user menu.

dac/base.html is the adapter between allauth's block vocabulary and
django-mvp's Account Center layout. The layout is django-mvp's; what these
tests cover is that a page extending this template arrives inside it, with the
entries this package contributes to the menu, and that allauth's own block
names still reach the page.

The sidebar user menu is django-mvp's <c-user.sidebar-menu> component; dac
integrates with it purely by registering the URL names it looks up
(account-center, account_logout). The tests here cover that integration
contract, not the component internals (those belong to django-mvp).
"""

import pathlib

import pytest
from django.urls import reverse

# Bare-minimum child template: extends base, loads i18n, no block overrides.
_BASE = '{% extends "dac/base.html" %}{% load i18n %}'


# ---------------------------------------------------------------------------
# dac/base.html — block contract and structure
# ---------------------------------------------------------------------------


def _account_nav(soup):
    """Every element django-mvp's account layout gives the navigation's name.

    The layout draws the menu at more than one site so it is reachable at every
    width, and how many is its own business, so these tests read all of them
    together rather than counting or picking one.
    """
    return soup.find_all(attrs={"aria-label": "Account navigation"})


def _account_nav_links(soup):
    return [a.get("href") or "" for nav in _account_nav(soup) for a in nav.find_all("a")]


class TestDacBaseBlockContract:
    def test_mvp_shell_sidebar_present(self, cotton_render_string_soup):
        """The mvp app shell renders untouched — dac must NOT replace the
        application sidebar (that was the pre-0.7 standalone-shell design)."""
        soup = cotton_render_string_soup(_BASE)
        assert soup.find("aside", class_="mvp-sidebar") is not None

    def test_account_navigation_present(self, cotton_render_string_soup):
        """A page extending this template arrives inside the Account Center,
        with the area's navigation beside it."""
        soup = cotton_render_string_soup(_BASE)
        assert _account_nav(soup) != []

    def test_account_menu_contains_overview_link(self, cotton_render_string_soup):
        """The menu links to the Account Center landing page."""
        soup = cotton_render_string_soup(_BASE)
        assert any("/account-center/" in href for href in _account_nav_links(soup))

    def test_account_menu_has_group_heading(self, cotton_render_string_soup):
        """The entries this package contributes are grouped under their own
        heading, which is what the group it appends carries."""
        soup = cotton_render_string_soup(_BASE)
        assert any("Email & Authentication" in nav.get_text() for nav in _account_nav(soup))

    def test_account_menu_contains_allauth_links(self, cotton_render_string_soup):
        """Email and password management items resolve to allauth URLs."""
        soup = cotton_render_string_soup(_BASE)
        hrefs = _account_nav_links(soup)
        assert any("email" in href for href in hrefs)
        assert any("password" in href for href in hrefs)

    def test_head_title_block_sets_document_title(self, cotton_render_string_soup):
        """{% block head_title %} feeds the HTML <title> (allauth contract)."""
        template = _BASE + "{% block head_title %}My Test Page{% endblock head_title %}"
        soup = cotton_render_string_soup(template)
        title_el = soup.find("title")
        assert title_el is not None
        assert "My Test Page" in title_el.get_text()

    def test_content_block_override_renders(self, cotton_render_string_soup):
        """{% block content %} content reaches the DOM (allauth pages fill it)."""
        template = _BASE + '{% block content %}<p id="my-content">Hello</p>{% endblock content %}'
        soup = cotton_render_string_soup(template)
        el = soup.find(id="my-content")
        assert el is not None
        assert el.get_text(strip=True) == "Hello"

    def test_extra_body_block_maps_to_page_end(self, cotton_render_string_soup):
        """{% block extra_body %} (allauth's script block) renders in the page."""
        template = _BASE + '{% block extra_body %}<script id="my-script"></script>{% endblock extra_body %}'
        soup = cotton_render_string_soup(template)
        assert soup.find(id="my-script") is not None


class TestDacBaseConsistency:
    def test_two_subpages_share_structure(self, cotton_render_string_soup):
        """Distinct sub-pages share the same structural anchors."""
        template_a = _BASE + "{% block head_title %}Page A{% endblock %}"
        template_b = _BASE + "{% block head_title %}Page B{% endblock %}"
        for template in (template_a, template_b):
            soup = cotton_render_string_soup(template)
            assert soup.find("aside", class_="mvp-sidebar") is not None
            assert _account_nav(soup) != []


class TestDacBaseStructure:
    def test_required_blocks_present_in_source(self):
        """dac/base.html defines the allauth-facing block contract."""
        template_path = (
            pathlib.Path(__file__).resolve().parent.parent.parent / "dac" / "templates" / "dac" / "base.html"
        )
        source = template_path.read_text(encoding="utf-8")
        for block_name in ["head_title", "extra_head", "extra_body", "content"]:
            assert f"{{% block {block_name} %}}" in source, f"Block '{block_name}' not found in dac/base.html"

    def test_manage_layout_extends_dac_base(self):
        """allauth's manage layout routes through dac/base.html."""
        template_path = (
            pathlib.Path(__file__).resolve().parent.parent.parent
            / "dac"
            / "allauth"
            / "templates"
            / "allauth"
            / "layouts"
            / "manage.html"
        )
        source = template_path.read_text(encoding="utf-8")
        assert '{% extends "dac/base.html" %}' in source


# ---------------------------------------------------------------------------
# Sidebar user menu (django-mvp's <c-user.sidebar-menu>) — integration
# ---------------------------------------------------------------------------

_USER_MENU = "<c-user.sidebar-menu />"


class TestUserSidebarMenuIntegration:
    """dac's contract with mvp's user menu: the account-center and
    account_logout URL names light the menu up; without them it degrades."""

    def test_anonymous_user_renders_nothing(self, cotton_render_string_soup):
        soup = cotton_render_string_soup(_USER_MENU)
        assert soup.find("div", class_="dropdown") is None
        assert soup.find("form", attrs={"method": "post"}) is None

    def test_authenticated_user_renders_dropdown(self, cotton_render_string_soup_authenticated):
        soup = cotton_render_string_soup_authenticated(_USER_MENU)
        assert soup.find("div", class_="dropdown") is not None

    def test_username_and_email_in_trigger(self, cotton_render_string_soup_authenticated):
        soup = cotton_render_string_soup_authenticated(_USER_MENU)
        trigger = soup.find(attrs={"role": "button"})
        assert trigger is not None
        assert "testuser" in trigger.get_text()
        assert "test@example.com" in trigger.get_text()

    def test_account_center_link_present(self, cotton_render_string_soup_authenticated):
        """FR: the Account Center item appears because dac registers the URL."""
        soup = cotton_render_string_soup_authenticated(_USER_MENU)
        links = soup.find_all("a")
        account_center_links = [a for a in links if "/account-center/" in (a.get("href") or "")]
        assert len(account_center_links) >= 1

    def test_logout_form_present(self, cotton_render_string_soup_authenticated):
        """Logout is a POST form targeting allauth's account_logout."""
        soup = cotton_render_string_soup_authenticated(_USER_MENU)
        form = soup.find("form", attrs={"method": "post", "id": "logoutForm"})
        assert form is not None
        assert "logout" in form.get("action", "")

    def test_account_center_link_absent_when_url_not_registered(
        self, settings, cotton_render_string_soup_authenticated
    ):
        settings.ROOT_URLCONF = "tests.urls_minimal"
        soup = cotton_render_string_soup_authenticated(_USER_MENU)
        links = soup.find_all("a")
        account_center_links = [a for a in links if "/account-center/" in (a.get("href") or "")]
        assert len(account_center_links) == 0

    def test_logout_form_absent_when_url_not_registered(self, settings, cotton_render_string_soup_authenticated):
        settings.ROOT_URLCONF = "tests.urls_minimal"
        soup = cotton_render_string_soup_authenticated(_USER_MENU)
        forms = soup.find_all("form", attrs={"method": "post"})
        assert len(forms) == 0

    def test_custom_slot_item_appears_before_logout(self, cotton_render_string_soup_authenticated):
        """Extra menu items passed via the slot render before the logout entry."""
        soup = cotton_render_string_soup_authenticated(
            """
            <c-user.sidebar-menu>
              <c-menu.item label="Settings" href="#" />
            </c-user.sidebar-menu>
            """
        )
        rendered_html = str(soup)
        settings_pos = rendered_html.find("Settings")
        logout_pos = rendered_html.find('id="logoutForm"')
        assert settings_pos != -1
        assert logout_pos != -1
        assert settings_pos < logout_pos


# ---------------------------------------------------------------------------
# dac/base.html — FR-008, a second Account Center integration
#
# ``dac.allauth`` is the only integration that has ever served a page through
# the shared management page. The tests below serve one from ``tests/testapp``
# — a plain installed app the core package knows nothing about — to prove the
# contract holds for any integration, not just the one that happens to exist.
#
# What this establishes: ``tests/testapp`` reaches ``dac/base.html`` purely by
# being an installed app that mounts its own URLs and registers its own menu
# group — no line of ``dac/`` was changed to make this work. What it does not
# establish: that a project can mount an integration's URLs *without* editing
# its own root URLconf. Automatic URL contribution is roadmap item R4 and is
# out of scope here.
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestSecondIntegrationServesManagementPage:
    """FR-008, scenario 1 — the test integration's own management view
    renders through the shared management page carrying the sub menu and its
    own content."""

    def test_response_is_successful(self, authenticated_client):
        response = authenticated_client.get(reverse("testapp_settings"))
        assert response.status_code == 200

    def test_sub_menu_present(self, authenticated_client):
        """The Account Center sub menu renders, carries the test integration's
        own group, and links back to the Account Center overview."""
        response = authenticated_client.get(reverse("testapp_settings"))
        content = response.content.decode()
        assert 'aria-label="Account navigation"' in content
        assert "Test App" in content
        assert f'href="{reverse("account-center")}"' in content

    def test_own_content_present(self, authenticated_client):
        """{% block content %} in testapp/settings.html reaches the page."""
        response = authenticated_client.get(reverse("testapp_settings"))
        content = response.content.decode()
        assert "Test App Settings" in content


@pytest.mark.django_db
class TestSecondIntegrationServesManagementPageWithoutAllauth:
    """FR-008, scenario 3 — the page still renders, and references no
    integration-owned template, when ``dac.allauth`` is absent.

    Uses the suite's existing minimal-URLconf isolation pattern rather than a
    new mechanism (see tests/test_components/test_dac_base.py's
    ``settings.ROOT_URLCONF = "tests.urls_minimal"`` tests): tests/urls_minimal.py
    mounts nothing dac-related at all, so it stands in for "dac.allauth
    absent" a fortiori — the test integration's own view still reaches the
    page with no dac URL, allauth or otherwise, registered.
    """

    def test_response_is_successful(self, authenticated_client, settings):
        settings.ROOT_URLCONF = "tests.urls_minimal"
        response = authenticated_client.get(reverse("testapp_settings"))
        assert response.status_code == 200

    def test_own_content_still_present(self, authenticated_client, settings):
        settings.ROOT_URLCONF = "tests.urls_minimal"
        response = authenticated_client.get(reverse("testapp_settings"))
        content = response.content.decode()
        assert "Test App Settings" in content

    def test_references_no_integration_template(self, authenticated_client, settings):
        """No template from ``dac.allauth`` (or any other integration) is
        used to render this page — it reaches ``dac/base.html`` and its own
        ``testapp/settings.html`` only."""
        settings.ROOT_URLCONF = "tests.urls_minimal"
        response = authenticated_client.get(reverse("testapp_settings"))
        template_names = {t.name for t in response.templates if t.name}
        integration_prefixes = ("account/", "allauth/", "dac/allauth/")
        offending = {name for name in template_names if name.startswith(integration_prefixes)}
        assert not offending
