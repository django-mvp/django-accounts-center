"""Account Center menu entries appear only for the people they apply to.

An integration attaches a visibility check to a menu entry it contributes,
and the entry is absent for anyone the check declines. These tests assert
what this package contributes: that an entry renders per person, that an
entry with no check stays visible, and that hiding one entry leaves the rest
of the page alone. That the check is called at all, and that a false result
hides an item, is django-flex-menus' behaviour and is tested there.
"""

import pytest
from anytree import PreOrderIter
from bs4 import BeautifulSoup
from django.urls import reverse
from flex_menu import root
from mvp import menus as mvp_menus

from dac import menus as dac_menus


def _menu_labels(response):
    """The set of menu-entry labels rendered in the Account Center nav.

    Every entry and group heading renders its label inside a ``<span>`` nested
    in an ``<li>`` (mvp's ``cotton/menu/item.html`` and
    ``cotton/menu/group.html``), inside the ``<ul>`` that ``c-menu`` renders
    with ``aria-label="Account navigation"``. django-mvp's account layout draws
    that menu at two sites — a dropdown below the sidebar breakpoint and a card
    above it — so both are collected and the set counts each label once. The
    ``<li>`` filter keeps out the dropdown's own toggle, which carries a
    ``<span>`` of its own without being a menu entry.
    """
    soup = BeautifulSoup(response.content, "html.parser")
    menus = soup.find_all(attrs={"aria-label": "Account navigation"})
    return {
        span.get_text(strip=True)
        for menu in menus
        for span in menu.find_all("span")
        if span.find_parent("li")
    }


@pytest.mark.django_db
class TestMenuDiffersByPerson:
    def test_menu_differs_in_exactly_the_gated_entry(self, gated_client, ungated_client):
        """Two people with the same installed apps read menus that differ in
        exactly the entry the visibility check applies to, and nothing else."""
        gated_labels = _menu_labels(gated_client.get(reverse("account-center")))
        ungated_labels = _menu_labels(ungated_client.get(reverse("account-center")))

        assert "Gated" in gated_labels
        assert "Gated" not in ungated_labels
        assert gated_labels - ungated_labels == {"Gated"}
        assert ungated_labels - gated_labels == set()


@pytest.mark.django_db
class TestGatedEntryVisibilityCheck:
    """FR-002: the visibility check an integration declares is asked on every
    request, not once when the menu is built. ``AccountCenterMenu`` is
    assembled at import, so the answer must not be captured at import, at
    sign-in, or in any cache in between. Not tested here: that ``check`` is
    called or that a false result hides an item — that is flex-menus' own
    behaviour (tasks.md Phase 3, "Not tested here"). That an entry is present
    for one person and absent for another is TestMenuDiffersByPerson.
    """

    def test_check_is_asked_again_when_the_answer_changes(self, ungated_client, ungated_person):
        """The same signed-in person, unchanged session, reads a different
        menu once the fact their entry's check consults changes."""
        from django.contrib.auth.models import Group

        from tests.testapp.menus import GATED_GROUP_NAME

        assert "Gated" not in _menu_labels(ungated_client.get(reverse("account-center")))

        group, _ = Group.objects.get_or_create(name=GATED_GROUP_NAME)
        ungated_person.groups.add(group)

        assert "Gated" in _menu_labels(ungated_client.get(reverse("account-center")))


@pytest.mark.django_db
class TestAllauthEntriesUnchanged:
    """FR-007: dac.allauth's own entries continue to appear exactly as they
    did before this feature, for a signed-in person. dac.allauth contributes
    no visibility check on any of its entries, so this is US-1's compatibility
    guarantee (FR-005) exercised against the one real integration shipped in
    this repo, not the test integration."""

    def test_allauth_entries_render_as_before(self, authenticated_client):
        response = authenticated_client.get(reverse("account-center"))
        labels = _menu_labels(response)
        assert {
            "Email",
            "Password",
            "Connected accounts",
            "Two-factor authentication",
            "Sessions",
        } <= labels


@pytest.mark.django_db
class TestUngatedEntryStaysVisible:
    """FR-005: an entry contributed with no visibility check stays visible
    whenever its integration is installed, regardless of who is looking —
    declaring a check is optional, and silence means visible."""

    def test_ungated_entry_present_for_both_people(self, gated_client, ungated_client):
        gated_labels = _menu_labels(gated_client.get(reverse("account-center")))
        ungated_labels = _menu_labels(ungated_client.get(reverse("account-center")))
        assert "Ungated" in gated_labels
        assert "Ungated" in ungated_labels


@pytest.mark.django_db
class TestPageUnaffectedByHiddenEntry:
    def test_other_entries_content_and_messages_render_the_same(self, gated_client, ungated_client):
        """The gated entry's own page renders the same for the person it is
        hidden from as for the person it applies to, apart from that one
        entry (FR-006): the other menu entries, the content region and the
        messages region are unaffected."""
        gated_response = gated_client.get(reverse("testapp_gated"))
        ungated_response = ungated_client.get(reverse("testapp_gated"))

        assert _menu_labels(gated_response) - {"Gated"} == _menu_labels(ungated_response)

        gated_soup = BeautifulSoup(gated_response.content, "html.parser")
        ungated_soup = BeautifulSoup(ungated_response.content, "html.parser")

        gated_h1 = gated_soup.find("h1")
        ungated_h1 = ungated_soup.find("h1")
        assert gated_h1 is not None
        assert gated_h1.get_text(strip=True) == "Test App Settings"
        assert ungated_h1 is not None
        assert ungated_h1.get_text(strip=True) == gated_h1.get_text(strip=True)

        gated_messages = gated_soup.find("div", class_="toast")
        ungated_messages = ungated_soup.find("div", class_="toast")
        assert gated_messages is not None
        assert ungated_messages is not None
        assert str(gated_messages) == str(ungated_messages)


class TestAccountCenterMenuIsSingular:
    """django-mvp ships the Account Center menu; this package adds to it.

    django-flex-menus holds every menu in one process-wide tree and looks one
    up by name, refusing to answer when two share it. A second menu declared
    here under the same name therefore does not shadow django-mvp's — it makes
    the name unresolvable, and every page that renders the menu raises instead.
    """

    def test_the_name_resolves_to_exactly_one_menu(self):
        """Looking the menu up by name answers, rather than raising because
        two menus in the tree claim the name."""
        assert root.get("AccountCenterMenu") is not None

    def test_the_menu_this_package_uses_is_the_one_django_mvp_ships(self):
        """Entries contributed here land on django-mvp's menu, so they show up
        on the pages django-mvp renders from it."""
        assert dac_menus.AccountCenterMenu is mvp_menus.AccountCenterMenu

    def test_this_package_declares_no_menu_of_its_own_under_that_name(self):
        """The whole tree holds one menu by that name, so no second
        declaration can reappear here unnoticed."""
        matches = [node for node in PreOrderIter(root) if node.name == "AccountCenterMenu"]
        assert len(matches) == 1
