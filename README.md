# Django Accounts Center

The account-management layer for [django-mvp](https://github.com/SamuelJennings/django-mvp)
projects. It gives a signed-in user one place to manage their account, and gives
you a way to put more things there as the project grows.

This package is not usable on its own. It renders on the django-mvp app shell
(DaisyUI 5 + Tailwind CSS v4 + django-cotton) and expects it.

## What it provides

- **An entrance layout.** Sign-in, sign-up and recovery pages render as a
  centered card with your site logo, outside the app shell.
- **An Account Center.** A management layout, a sub menu, and an overview page
  whose cards come from whatever you have installed.
- **An integration system.** The machinery that lets a third-party app add its
  own account-management pages to that Account Center.

## Integrations

An integration is a gated sub-app that teaches the Account Center about one
third-party package. You enable one by adding it to `INSTALLED_APPS`:

```python
INSTALLED_APPS = ["dac", "dac.allauth", ...]   # future: "dac.stripe", …
```

From there the integration contributes its own labelled menu group, any
overview cards it needs (through the `dac_overview_template` and
`dac_overview_context` hooks on its `AppConfig`), and its template overrides.
What is installed decides which contributions exist.

Because every integration is gated, a project carries only the dependencies of
the integrations it turns on. Installing this package pulls in nothing you have
not enabled.

Shipped today: `dac.allauth`, and it is the only one. Two limitations are worth
knowing before you write your own: an integration's URLs are still mounted by
the core app rather than contributed by the integration, and menu entries and
cards are decided once at startup rather than per visitor.

## The allauth integration

`dac.allauth` does **not** fork allauth's page templates. It overrides allauth's
three **layouts** and its ~22 **element** templates:

- `allauth/layouts/entrance.html` — login, signup, password reset, sign-in
  codes, … render as a centered card (no app shell) with your site logo.
- `allauth/layouts/manage.html` → `dac/base.html` — email, password, MFA,
  sessions and connected-accounts pages render inside the normal django-mvp
  shell with an "Account Center" sub menu beside the content.
- `allauth/elements/*.html` — every `{% element %}` (button, field, form,
  panel, alert, badge, provider button, table, …) maps to DaisyUI markup.

Because allauth's own stock page templates do the rendering, **every allauth
feature and configuration variation works automatically** — passkeys,
login-by-code, email verification by code, phone numbers, `SOCIALACCOUNT_ONLY`,
MFA (TOTP / WebAuthn / recovery codes / trust), user sessions — now and in
future allauth releases. On top of that it contributes overview cards for
email, password, 2FA, sessions and connected accounts, and a menu group whose
items appear only for the allauth apps you install.

The core `dac` app adds the pieces that are not allauth's business: the Account
Center overview page (`account-center` URL), a `DAC_ICONS` easy-icons pack, and
a prebuilt `dac.css` stylesheet. The `AccountCenterMenu` the integrations append
to is django-mvp's, re-exported from `dac.menus` so either import reaches the
same menu. django-mvp's `<c-user.sidebar-menu>` picks up an "Account Center"
entry and a POST logout form once the URLs are installed.

## Scope

This package is deliberately narrow.

- **It requires django-mvp.** Account management was taken out of django-mvp
  core so it could be maintained on its own, not so it could be used
  elsewhere. There is no standalone mode.
- **It does not provide authentication.** allauth does that. This package
  presents it.
- **It is not a plugin marketplace.** The integration pattern is open, so
  write one for your own project's apps whenever you need to. The set that
  ships here is curated: an integration is bundled only when it has broad
  appeal, a clear purpose, and a well-maintained package behind it. Anything
  narrower belongs in the project that needs it.

The goals this package steers toward are recorded in [GOALS.md](GOALS.md).

## Installation

```bash
pip install django-accounts-center[allauth]
```

### 1. Settings

```python
INSTALLED_APPS = [
    # ...
    "django.contrib.sites",
    "dac",
    "dac.allauth",              # BEFORE allauth so template overrides win
    "mvp",
    "allauth",
    "allauth.account",
    "allauth.socialaccount",    # optional
    "allauth.mfa",              # optional
    "allauth.usersessions",     # optional
    "easy_icons",
    "flex_menu",
    "django_cotton",
    # ...
]

SITE_ID = 1

MIDDLEWARE = [
    # ...
    "allauth.account.middleware.AccountMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

TEMPLATES = [{
    # ...
    "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request",
        # ...
        "mvp.context_processors.mvp_config",
    ]},
}]

# django-mvp shell: show the user menu at the bottom of the sidebar.
MVP_CONFIG = {
    "layout": {
        "sidebar": {"footer": ["user.sidebar-menu"]},
    },
}

# Icons: mvp's Bootstrap Icons pack + dac's account icons.
EASY_ICONS = {
    "default": {
        "renderer": "easy_icons.renderers.ProviderRenderer",
        "config": {"tag": "i"},
        "packs": ["mvp.utils.BS5_ICONS", "dac.icons.DAC_ICONS"],
    },
}

FLEX_MENUS = {
    "renderers": {
        "sidebar": "mvp.renderers.SidebarRenderer",
        "dock": "mvp.renderers.MobileFooterNavRenderer",
    },
}

LOGIN_URL = "account_login"
LOGIN_REDIRECT_URL = "/accounts/"
```

### 2. URLs

dac's URLconf includes `allauth.urls` for you — mount it once:

```python
urlpatterns = [
    path("accounts/", include("dac.urls")),
    # ...
]
```

This registers the `account-center` overview page at `/accounts/` plus all of
allauth's URLs (`/accounts/login/`, `/accounts/email/`, `/accounts/2fa/`, …).

### 3. Migrate

```bash
python manage.py migrate
```

That's it. Anonymous users get centered entrance pages. Authenticated users
reach the Account Center from the user menu at the bottom of the sidebar.

## Customisation

- **Re-skin everything**: override any `allauth/elements/*.html` template in
  your project — it applies across all allauth pages at once.
- **Page-level tweaks**: override individual allauth page templates the normal
  Django way (your project templates win over dac's and allauth's). Prefer
  element overrides — per-page forks are what this package exists to avoid.
- **Entrance pages**: give your own app a signed-out page by extending
  `dac/entrance.html` and filling `{% block content %}`. It brings the same
  chrome dac's own signed-out pages use. For a wider card, override
  `{% block entrance %}` instead, wrapping `<c-dac.entrance size="full">`
  around your `{% block content %}` — the content block moves inside the
  override, because a template can declare a block only once. The default
  width and `full` are the only two until
  [django-mvp#126](https://github.com/django-mvp/django-mvp/issues/126)
  widens the underlying component.
- **Sub menu**: append items (or a labelled `mvp.menus.MenuGroup`) to
  `dac.menus.AccountCenterMenu` from your own `menus.py` (e.g. a profile-edit
  page). Items may declare `url_names` prefixes in `extra_context` so
  breadcrumbs resolve their sub-pages.
- **Overview page**: subclass `dac.views.AccountCenterView` and point the
  `account-center` URL at it, or override `dac/account_center.html`.
- **Social login icons**: `dac.allauth` ships brand SVGs for the major
  providers (Google, GitHub, Microsoft, Apple, Facebook, X, LinkedIn, GitLab,
  Discord, ORCID) in its `icons/` template dir. Register them under a
  django-easy-icons `"svg"` renderer keyed by allauth provider id (see the
  example `EASY_ICONS` setting). `provider.html` renders them with
  `{% icon provider_id renderer="svg" %}`, so a provider without a registered
  icon raises `IconNotFound` (caught in development, not shipped broken), and
  any icon is overridable via your `EASY_ICONS` config or a template shadow.
- **Styling**: dac ships a prebuilt `dac.css` (Tailwind v4 + DaisyUI 5 over
  both mvp's and dac's templates). If your project runs its own Tailwind
  build, add dac's templates as a source alongside mvp's (see
  `assets/tailwind.css`) and override the `styles` block.

## Development

```bash
git clone https://github.com/SamuelJennings/django-accounts-center.git
cd django-accounts-center
poetry install
npm install

# run the example project
python manage.py runserver

# rebuild the shipped stylesheet after template changes
npm run build:css

# tests
pytest
```

The `example/` project exercises an aggressive allauth configuration
(passkeys, login-by-code, email verification by code, MFA, three social
providers) and `tests/` includes an architecture guard
(`tests/test_architecture.py`) that fails if anyone reintroduces per-page
allauth template forks.

## License

MIT
