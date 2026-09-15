"""Icon pack for django-accounts-center.

Registered with django-easy-icons via the ``packs`` mechanism, on top of
django-mvp's ``BS5_ICONS`` (which already provides login, logout, email,
delete, warning, success, etc.):

    EASY_ICONS = {
        "default": {
            "renderer": "easy_icons.renderers.ProviderRenderer",
            "config": {"tag": "i"},
            "packs": ["mvp.utils.BS5_ICONS", "dac.icons.DAC_ICONS"],
        },
    }

Comma-separated keys register aliases for the same glyph.
"""

DAC_ICONS = {
    # ── Account Center navigation ────────────────────────────────────────
    # account_center and overview belong to django-mvp's pack, which owns the
    # Account Center itself and maps both to the same glyphs this pack used to.
    # Repeating them here only reassigns a name this pack agrees with, which
    # django-easy-icons reports as a collision.
    "password": "bi bi-lock-fill",
    "password_change": "bi bi-key-fill",
    "mfa, two_factor, security": "bi bi-shield-lock",
    "sessions, devices": "bi bi-display",
    "social, connections": "bi bi-people",
    # ── Auth flows ───────────────────────────────────────────────────────
    "passkey": "bi bi-fingerprint",
    "passcode, code": "bi bi-123",
    "send": "bi bi-send",
    "resend, refresh": "bi bi-arrow-clockwise",
    "cancel": "bi bi-x-circle",
    "signup": "bi bi-person-plus",
    # ── UI ───────────────────────────────────────────────────────────────
    "chevron_down": "bi bi-chevron-down",
    # ── Status ───────────────────────────────────────────────────────────
    "verified": "bi bi-patch-check-fill",
    "unverified": "bi bi-patch-exclamation",
    "recovery_codes": "bi bi-life-preserver",
    "totp, authenticator_app": "bi bi-qr-code",
}
