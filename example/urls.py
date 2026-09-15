from django.contrib import admin
from django.contrib.auth import get_user_model
from django.urls import include, path, reverse_lazy
from django.views.generic.base import RedirectView
from django.views.generic.edit import UpdateView

from example.views import EmailChangeTestView, _verified_email_required_view

urlpatterns = [
    path("", RedirectView.as_view(url=reverse_lazy("account_login")), name="example-home"),
    # The landing page is django-mvp's; dac.urls adds the installed
    # integrations' pages at the same prefix.
    path("account-center/", include("mvp.urls")),
    path("account-center/", include("dac.urls")),
    path(
        "profile/<pk>/",
        UpdateView.as_view(model=get_user_model(), fields=["username", "first_name", "last_name"]),
        name="profile-edit",
    ),
    path("admin/", admin.site.urls),
    # Test-only URLs — not part of the production URL configuration
    path(
        "test/email-change/",
        EmailChangeTestView.as_view(),
        name="account_email_change_test",
    ),
    path(
        "test/verified-email-required/",
        _verified_email_required_view,
        name="account_verified_email_required",
    ),
    path("__reload__/", include("django_browser_reload.urls")),
]
