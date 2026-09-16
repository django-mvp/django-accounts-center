"""System check warning when a project turns off allauth's safe GET defaults.

Signing out by GET and confirming an email address by GET are both off by
default in allauth, because both let a browser or a mail gateway that merely
follows a link trigger something a person didn't ask for: ending a session, or
consuming an email confirmation. A project that flips either back on gets a
warning at startup, not an incident.
"""

from django.core.checks import run_checks
from django.test import override_settings

from dac.allauth.checks import check_unsafe_get_settings


class TestCheckUnsafeGetSettings:
    def test_no_warnings_at_allauth_defaults(self):
        assert check_unsafe_get_settings(None) == []

    @override_settings(ACCOUNT_LOGOUT_ON_GET=True)
    def test_warns_when_logout_on_get_is_enabled(self):
        warnings = check_unsafe_get_settings(None)
        assert [w.id for w in warnings] == ["dac_allauth.W001"]

    @override_settings(ACCOUNT_CONFIRM_EMAIL_ON_GET=True)
    def test_warns_when_confirm_email_on_get_is_enabled(self):
        warnings = check_unsafe_get_settings(None)
        assert [w.id for w in warnings] == ["dac_allauth.W002"]

    @override_settings(ACCOUNT_LOGOUT_ON_GET=True, ACCOUNT_CONFIRM_EMAIL_ON_GET=True)
    def test_warns_for_both_when_both_are_enabled(self):
        warnings = check_unsafe_get_settings(None)
        assert {w.id for w in warnings} == {"dac_allauth.W001", "dac_allauth.W002"}

    @override_settings(ACCOUNT_LOGOUT_ON_GET=True)
    def test_check_is_registered_and_runs_via_manage_py_check(self):
        warnings = run_checks()
        assert "dac_allauth.W001" in [w.id for w in warnings]
