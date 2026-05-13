import importlib.util
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "example-not-for-production"
DEBUG = True

# Hosts the demo recognises. example.com and mac-mini are the two demo sites
# created by `manage.py seed_demo`. Add them to /etc/hosts (or use curl
# --resolve) to actually reach them on this machine.
ALLOWED_HOSTS = ["example.com", "mac-mini", "localhost", "127.0.0.1"]

# No SITE_ID on purpose. With CurrentSiteMiddleware enabled, Django will look
# up the Site by the request's Host header, so visiting example.com and
# mac-mini serves different content from the same server.

# Optional rich text editor for the admin. Set RICH_EDITOR=1 in the
# environment and install `django-tinymce` (see example/README.md) to
# swap the plain <textarea> for a TinyMCE editor on the Article form.
RICH_EDITOR = os.environ.get("RICH_EDITOR", "").lower() in ("1", "true", "yes")

INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.admin",
    "django.contrib.staticfiles",
    "siteblog",
    "example_project",
]

if RICH_EDITOR:
    # `django-tinymce` is an optional extras dependency. Probe for it
    # before adding to INSTALLED_APPS so we can fail with a clear message
    # instead of a Django app-registry traceback.
    if importlib.util.find_spec("tinymce") is None:
        raise ImproperlyConfigured(
            "RICH_EDITOR=1 is set but the optional `django-tinymce` "
            "package is not installed. Install it via the project's "
            "extras:\n\n"
            "    uv sync --extra rich-editor\n\n"
            "or, from inside an activated virtualenv:\n\n"
            "    uv pip install django-tinymce\n\n"
            "Alternatively, unset RICH_EDITOR to use the plain textarea."
        )
    INSTALLED_APPS.append("tinymce")

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]

ROOT_URLCONF = "example_project.urls"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

STATIC_URL = "/static/"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
USE_TZ = True

# Minimal TinyMCE config matching the kinds of HTML the demo articles
# already render (bold/italic/headings/lists/links/code/blockquote).
TINYMCE_DEFAULT_CONFIG = {
    "height": 400,
    "menubar": False,
    "plugins": "lists link code",
    "toolbar": (
        "undo redo | h2 h3 | bold italic | bullist numlist | blockquote link | code"
    ),
}
