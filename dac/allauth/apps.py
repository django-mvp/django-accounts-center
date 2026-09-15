from django.apps import AppConfig


class DacAllauthConfig(AppConfig):
    """django-allauth integration for the Account Center.

    Opt in by adding ``"dac.allauth"`` to ``INSTALLED_APPS``, **before both
    ``"allauth"`` and ``"mvp"``**. App template directories are searched in
    that order, and this app overrides a template belonging to each of them:
    allauth's layouts and elements, and django-mvp's Account Center landing
    page, which is how its overview cards reach the page.

    It contributes its cards by shipping ``mvp/account/overview.html`` and
    adding to that template's card block, which is django-mvp's documented
    extension point. There is no attribute to declare here for it.
    """

    name = "dac.allauth"
    label = "dac_allauth"
    verbose_name = "Account Center — allauth"
