"""
Test-specific Django settings.

This module provides a stable, minimal configuration for testing that won't be
affected by changes to example.settings during development.

Tests should use this as the base configuration and override specific settings
when testing optional features like passkeys, MFA, or social login.
"""

from pathlib import Path

from example.settings import EASY_ICONS, FLEX_MENUS, MVP_CONFIG  # noqa: F401

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent

SECRET_KEY = "test-secret-key-for-testing-only"

DEBUG = True

ALLOWED_HOSTS = ["*"]

USE_I18N = True

# Minimal app configuration for testing
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.sites",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "example",
    "dac",
    "dac.allauth",
    "tests.testapp",
    "mvp",
    "daisy_cotton",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.github",
    "allauth.mfa",
    "allauth.usersessions",
    "easy_icons",
    "crispy_forms",
    "mvp_forms",
    "flex_menu",
    "django_cotton",
]

CRISPY_ALLOWED_TEMPLATE_PACKS = ["daisyui"]
CRISPY_TEMPLATE_PACK = "daisyui"

SITE_ID = 1

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "tests.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "mvp.context_processors.mvp_config",
            ],
        },
    },
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",  # Use in-memory database for faster tests
    }
}

AUTH_PASSWORD_VALIDATORS = []

STATIC_URL = "/static/"
STATIC_ROOT = str(BASE_DIR / "static")

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

STORAGES = {
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    },
}

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

# ======= Basic Allauth Settings for Tests =======
# Tests start with username/password authentication only
# Individual tests can override these to test optional features

# Basic authentication - username or email
ACCOUNT_LOGIN_METHODS = {"username", "email"}

# No email verification by default (tests can override)
ACCOUNT_EMAIL_VERIFICATION = "none"

# MFA_PASSKEY_LOGIN_ENABLED is True so that allauth.mfa.webauthn.urls registers
# mfa_login_webauthn at import time (the URL list is built once on first import,
# before any per-test settings override can take effect).
# Tests that need passkey login *disabled* should still set
# settings.MFA_PASSKEY_LOGIN_ENABLED = False, which controls runtime behaviour
# (template rendering, view guards) even though the URL is always registered.
MFA_PASSKEY_LOGIN_ENABLED = True
MFA_PASSKEY_SIGNUP_ENABLED = True
MFA_SUPPORTED_TYPES = ["totp", "webauthn", "recovery_codes"]
MFA_WEBAUTHN_ALLOW_INSECURE_ORIGIN = True
ACCOUNT_LOGIN_BY_CODE_ENABLED = True


# Email backend for testing
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# URL configuration
LOGIN_URL = "/"
LOGIN_REDIRECT_URL = "/account-center/"

# # EASY_ICONS and FLEX_MENUS are imported from example.settings at the top of this file.
# PARLER_LANGUAGES = {
#     None: ({"code": "en"},),
#     "default": {
#         "fallbacks": ["en"],
#         "hide_untranslated": False,
#     },
# }
