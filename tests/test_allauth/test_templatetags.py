"""The filters the allauth overview cards read their data through.

Both take a queryset the card is already walking and answer one question about
it. The cards themselves are covered in ``test_overview_cards``; these pin the
two rules that are easy to get subtly wrong.
"""

import pytest
from allauth.mfa.models import Authenticator

from dac.allauth.templatetags.dac_allauth import has_second_factor, unverified_count


class _Address:
    def __init__(self, verified):
        self.verified = verified


class _Authenticator:
    def __init__(self, type):
        self.type = type


class TestUnverifiedCount:
    def test_counts_only_the_unverified(self):
        addresses = [_Address(True), _Address(False), _Address(False)]
        assert unverified_count(addresses) == 2

    def test_zero_when_every_address_is_verified(self):
        assert unverified_count([_Address(True), _Address(True)]) == 0

    def test_zero_for_an_account_with_no_address(self):
        assert unverified_count([]) == 0


class TestHasSecondFactor:
    @pytest.mark.parametrize(
        "type_",
        [Authenticator.Type.TOTP, Authenticator.Type.WEBAUTHN],
    )
    def test_true_for_a_factor_a_person_signs_in_with(self, type_):
        assert has_second_factor([_Authenticator(type_)]) is True

    def test_false_for_recovery_codes_alone(self):
        """Recovery codes are the way back in when the second factor is
        unavailable. An account holding only those has not turned two-factor
        sign-in on, and a card saying otherwise would be telling someone they
        are protected when they are not."""
        assert has_second_factor([_Authenticator(Authenticator.Type.RECOVERY_CODES)]) is False

    def test_true_when_recovery_codes_sit_beside_a_real_factor(self):
        authenticators = [
            _Authenticator(Authenticator.Type.RECOVERY_CODES),
            _Authenticator(Authenticator.Type.TOTP),
        ]
        assert has_second_factor(authenticators) is True

    def test_false_when_nothing_is_set_up(self):
        assert has_second_factor([]) is False
