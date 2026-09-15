"""
Test URL configuration for integration tests.

Provides allauth account URLs without debug_toolbar or other
development-only dependencies.
"""

from django.contrib import admin
from django.shortcuts import render
from django.urls import include, path

from example.views import EmailChangeTestView, MultiEmailTestView, _verified_email_required_view


def _user_menu_no_avatar_view(request):
    return render(request, "test_user_menu_no_avatar.html")


def _user_menu_photo_view(request):
    return render(request, "test_user_menu_photo.html")


def _user_menu_custom_view(request):
    return render(request, "test_user_menu_custom.html")


class _MockAlternative:
    url = "/accounts/mock-mfa/"
    description = "Use authenticator code"


def _reauthenticate_with_alternatives_view(request):
    from allauth.account.forms import ReauthenticateForm

    form = ReauthenticateForm(user=request.user) if request.user.is_authenticated else None
    return render(
        request,
        "account/reauthenticate.html",
        {
            "form": form,
            "reauthentication_alternatives": [_MockAlternative()],
        },
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    # The landing page is django-mvp's, mounted from mvp.urls; dac.urls adds
    # the installed integrations' pages at the same prefix. dac.urls includes
    # allauth.urls, so mounting allauth separately would register every allauth
    # URL name twice and resolve by last registration.
    path("account-center/", include("mvp.urls")),
    path("account-center/", include("dac.urls")),
    # Test-only URLs — not part of the production URL configuration
    path("test/testapp/", include("tests.testapp.urls")),
    path(
        "test/email-change/",
        EmailChangeTestView.as_view(),
        name="account_email_change_test",
    ),
    path(
        "test/email-multi/",
        MultiEmailTestView.as_view(),
        name="account_email_multi_test",
    ),
    path(
        "test/verified-email-required/",
        _verified_email_required_view,
        name="account_verified_email_required",
    ),
    path(
        "test/reauthenticate-alternatives/",
        _reauthenticate_with_alternatives_view,
        name="test_reauthenticate_alternatives",
    ),
    # Name alias so allauth's stock confirm_password_reset_code.html can
    # reverse its action URL when rendered directly by template tests.
    # (allauth only registers this name when
    # ACCOUNT_PASSWORD_RESET_BY_CODE_ENABLED is True at import time, but
    # enabling that globally would switch the whole reset flow to code mode
    # and break the link-flow tests.)
    path(
        "test/confirm-password-reset-code/",
        _verified_email_required_view,
        name="account_confirm_password_reset_code",
    ),
    # User menu screenshot test URLs
    path("test/user-menu/no-avatar/", _user_menu_no_avatar_view, name="test_user_menu_no_avatar"),
    path("test/user-menu/photo/", _user_menu_photo_view, name="test_user_menu_photo"),
    path("test/user-menu/custom/", _user_menu_custom_view, name="test_user_menu_custom"),
]
