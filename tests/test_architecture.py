"""Architecture guardrails for the elements-first allauth integration.

Since 0.7, dac deliberately does NOT fork allauth's page templates. Styling
is applied through the allauth layouts (allauth/layouts/*.html) and elements
(allauth/elements/*.html) only, so that every allauth page — current and
future, under every configuration — renders through allauth's own stock
templates. Any per-page override must be a conscious, documented exception
added to PAGE_OVERRIDE_ALLOWLIST.
"""

import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
DAC_CORE_TEMPLATES = REPO_ROOT / "dac" / "templates"
DAC_ALLAUTH_TEMPLATES = REPO_ROOT / "dac" / "allauth" / "templates"

# Per-page allauth template overrides dac is allowed to ship. Add entries
# only when the element system genuinely cannot express the desired UX.
PAGE_OVERRIDE_ALLOWLIST = {
    "account/snippets/warn_no_email.html",
}

EXPECTED_ELEMENTS = {
    "alert",
    "badge",
    "button",
    "button_group",
    "details",
    "field",
    "fields",
    "form",
    "h1",
    "h2",
    "hr",
    "img",
    "p",
    "panel",
    "provider",
    "provider_list",
    "table",
    "tbody",
    "td",
    "th",
    "thead",
    "tr",
}


def test_no_unexpected_page_template_forks():
    """dac must not fork allauth page templates outside the allowlist."""
    forked = set()
    for templates_root in (DAC_CORE_TEMPLATES, DAC_ALLAUTH_TEMPLATES):
        for app_dir in ("account", "socialaccount", "mfa", "usersessions", "openid", "idp"):
            root = templates_root / app_dir
            if not root.exists():
                continue
            for path in root.rglob("*.html"):
                forked.add(str(path.relative_to(templates_root)).replace("\\", "/"))
    unexpected = forked - PAGE_OVERRIDE_ALLOWLIST
    assert not unexpected, (
        f"Unexpected allauth page template forks: {sorted(unexpected)}. "
        "Style via allauth/elements/ instead, or add a documented allowlist entry."
    )


def test_allauth_templates_live_in_the_gated_subapp():
    """The allauth skin ships in dac.allauth, never in the core dac app —
    hosts opt in by installing "dac.allauth"."""
    assert not (DAC_CORE_TEMPLATES / "allauth").exists()
    assert (DAC_ALLAUTH_TEMPLATES / "allauth").exists()


def test_all_elements_overridden():
    """Every allauth element template has a dac override."""
    elements_dir = DAC_ALLAUTH_TEMPLATES / "allauth" / "elements"
    present = {p.stem for p in elements_dir.glob("*.html")}
    missing = EXPECTED_ELEMENTS - present
    assert not missing, f"Missing element overrides: {sorted(missing)}"


def test_layouts_overridden():
    """Both allauth layouts (plus the base fallback) have dac overrides."""
    layouts_dir = DAC_ALLAUTH_TEMPLATES / "allauth" / "layouts"
    present = {p.stem for p in layouts_dir.glob("*.html")}
    assert {"base", "entrance", "manage"} <= present


def test_allauth_entrance_layout_delegates_its_chrome():
    """The allauth entrance layout (dac/allauth/templates/allauth/layouts/entrance.html)
    must be a thin block-mapping shim over the core-owned dac/entrance.html: it
    extends that page and keeps only the allauth block mapping, with no card,
    background or logo markup of its own."""
    path = DAC_ALLAUTH_TEMPLATES / "allauth" / "layouts" / "entrance.html"
    source = path.read_text(encoding="utf-8")
    assert '{% extends "dac/entrance.html" %}' in source
    for forbidden in ("c-entrance", "c-messages", "<img", "logo_url", "{% block app %}", "{% block styles %}"):
        assert forbidden not in source, (
            f"{path.relative_to(DAC_ALLAUTH_TEMPLATES.parent.parent)} still authors '{forbidden}' "
            "directly instead of delegating to dac/entrance.html"
        )


def test_core_entrance_templates_reference_no_integration():
    """The shared entrance page (dac/templates/dac/entrance.html) and its
    component (dac/templates/cotton/dac/entrance.html) must stand up with no
    integration installed, so neither may reference a template path under an
    integration sub-app — dac/allauth/ today, or any future dac/<package>/."""
    dac_root = DAC_CORE_TEMPLATES.parent
    integrations = {p.name for p in dac_root.iterdir() if p.is_dir() and (p / "templates").exists()}
    entrance_files = (
        DAC_CORE_TEMPLATES / "dac" / "entrance.html",
        DAC_CORE_TEMPLATES / "cotton" / "dac" / "entrance.html",
    )
    for path in entrance_files:
        source = path.read_text(encoding="utf-8")
        for integration in integrations:
            assert integration not in source, (
                f"{path.relative_to(dac_root.parent)} references integration '{integration}'"
            )


class TestVisualLayerBelongsToDjangoMvp:
    """Constitution Article XVII, as a gate rather than a convention."""

    def test_package_ships_no_stylesheet_or_frontend_build(self):
        """The visual layer belongs to django-mvp (constitution Article XVII).

        This package composes mvp's components and the DaisyUI utilities they are
        built from, and ships neither CSS of its own nor a toolchain to produce
        any. A stylesheet here would be a second place for a design decision to
        live, and a build step would be a second toolchain for a consumer to
        reason about.

        The gate is the artefact, not the intent: a `.css` file under the package,
        or a `package.json` at the root, is what a reviewer would otherwise have to
        notice by eye.
        """
        stylesheets = sorted(p.relative_to(REPO_ROOT).as_posix() for p in (REPO_ROOT / "dac").rglob("*.css"))
        assert stylesheets == [], f"this package ships CSS of its own: {stylesheets}"

        for artefact in ("package.json", "package-lock.json", "assets"):
            assert not (REPO_ROOT / artefact).exists(), (
                f"{artefact} is back — the front-end build belongs to django-mvp"
            )

    def test_no_template_overrides_the_stylesheet_block(self):
        """Every page reaches django-mvp's stylesheet by leaving `styles` alone.

        Overriding that block without calling `block.super` is how a page ends up
        with no stylesheet at all, and it renders as an unstyled page rather than
        as an error — so nothing else would catch it.
        """
        offenders = [
            path.relative_to(REPO_ROOT).as_posix()
            for path in (REPO_ROOT / "dac").rglob("*.html")
            if "{% block styles %}" in path.read_text(encoding="utf-8")
        ]
        assert offenders == [], f"templates overriding the styles block: {offenders}"
