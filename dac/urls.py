"""The URLs this package's integrations serve.

The Account Center's own landing page is not here. django-mvp ships it as
``mvp.urls``, and a project mounts that itself at whatever prefix it wants —
including it from here would decide that address on the project's behalf, and
register a second view under the ``account-center`` name for any project that
had already mounted it.

A project therefore mounts both, at the same prefix::

    urlpatterns = [
        path("accounts/", include("mvp.urls")),
        path("accounts/", include("dac.urls")),
    ]
"""

from django.urls import include, path
from mvp.utils import app_is_installed

urlpatterns = []

if app_is_installed("dac.allauth"):
    urlpatterns.append(path("", include("dac.allauth.urls")))
