"""The URLs this package's integrations serve.

The Account Center's own landing page is not here. django-mvp ships it as
``mvp.urls``, and a project mounts that itself — including it from here would
register a second view under the ``account-center`` name for any project that
had already mounted it.

django-mvp serves the landing page under ``account/``, so a project mounts its
URLconf at the site root and this one at ``account/`` to keep the pages
together::

    urlpatterns = [
        path("", include("mvp.urls")),
        path("account/", include("dac.urls")),
    ]
"""

from django.urls import include, path
from mvp.utils import app_is_installed

urlpatterns = []

if app_is_installed("dac.allauth"):
    urlpatterns.append(path("", include("dac.allauth.urls")))
