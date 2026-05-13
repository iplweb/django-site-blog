# django-site-blog

[![Tests](https://github.com/iplweb/django-site-blog/actions/workflows/tests.yml/badge.svg)](https://github.com/iplweb/django-site-blog/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://github.com/iplweb/django-site-blog)
[![Django](https://img.shields.io/badge/django-5.2%20LTS%20%7C%206.0-0c4b33)](https://github.com/iplweb/django-site-blog)
[![License](https://img.shields.io/github/license/iplweb/django-site-blog)](LICENSE)

Small Django blog / news app with multi-site support
(`django.contrib.sites`).

Lets editors restrict an article to one or more `Site` objects, or
leave the assignment empty so the article appears on every site that
runs the same Django project.

## Why?

Many Django projects host multiple sites — a corporate front page, a
research portal, project subsites — from a single codebase using
`django.contrib.sites`. Most blog/news apps either ignore that scenario
or expect a separate deployment per site.

`django-site-blog` keeps one article store and lets editors say, per
article, whether it should appear on _every_ site (the default) or be
restricted to a chosen subset. One schema, one query, no middleware
gymnastics.

## Features

- Per-article site assignment via M2M to `django.contrib.sites.models.Site`.
- "Empty M2M = visible everywhere" default — restrict only when you need to.
- `draft`/`published` status via `model_utils.StatusModel`; admin-aware
  `get_absolute_url` so drafts link back into the admin.
- Split-marker excerpts via `model_utils.SplitField`
  (marker configurable through the `SPLIT_MARKER` setting).
- Multi-site-aware `ArticleDetailView` (slug-based, filters by `SITE_ID`).
- `Article.on_site` `CurrentSiteManager` for pure
  "current-site only" semantics when the empty-equals-all default isn't
  what you want.
- Polish translation included; rest of the UI is `gettext_lazy`-ready.
- Admin with `filter_horizontal`, `list_filter`, slug prepopulation.

## Supported versions

### Django × Python

| Django  | 3.10 | 3.11 | 3.12 | 3.13 | 3.14 | Status                                  |
|---------|------|------|------|------|------|-----------------------------------------|
| 5.2 LTS | ✓    | ✓    | ✓    | ✓    | ✓    | Active LTS (extended support Apr 2028)  |
| 6.0     | —    | —    | ✓    | ✓    | ✓    | Mainstream Aug 2026, extended Apr 2027  |

Verified against the CI matrix in
[`.github/workflows/tests.yml`](.github/workflows/tests.yml). Also
requires [django-model-utils](https://pypi.org/project/django-model-utils/)
`>=4.5,<5` (for `SplitField`, `TimeStampedModel`, `StatusModel`).
The 5.x release of `django-model-utils` changed `SplitField` in a way that
conflicts with explicit `_article_body_excerpt` declarations in migrations
(produces a duplicate-column error at `migrate`); the upper bound is
deliberate until upstream resolves it.

## Installation

```bash
uv add django-site-blog
```

or with pip:

```bash
pip install django-site-blog
```

Add the app and `django.contrib.sites` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "django.contrib.sites",
    "siteblog",
]

SITE_ID = 1  # required by django.contrib.sites
```

Include the URLs in your project's `urls.py`:

```python
urlpatterns = [
    # ...
    path("articles/", include("siteblog.urls")),
]
```

Run migrations:

```bash
python manage.py migrate
```

## How site assignment works

Each `Article` has a `sites` M2M to `django.contrib.sites.models.Site`.

- **Empty M2M** → article visible on every site (the default).
- **One or more sites set** → article only visible on the listed sites.

The included `ArticleDetailView` enforces this with a single OR query:

```python
Article.objects.filter(
    Q(sites__isnull=True) | Q(sites__id=settings.SITE_ID)
).distinct()
```

If you want pure "current-site only" semantics (drop the empty-equals-all
behaviour), use the `Article.on_site` `CurrentSiteManager` instead.

## Settings

| Setting | Default | Purpose |
|---|---|---|
| `SITE_ID` | — | Required by `django.contrib.sites`. Drives the per-site filtering. |
| `SPLIT_MARKER` | `"<!-- split -->"` | Marker shown in the admin help text for `Article.article_body` to indicate the split-point between excerpt and full article. The actual splitting is performed by `model_utils.fields.SplitField` per its own settings. |

## Templates

The package ships two minimal templates:

- `siteblog/article_detail.html` — uses `{% extends "siteblog/base.html" %}`.
- `siteblog/base.html` — a bare HTML skeleton; override it in your
  project by placing a `siteblog/base.html` ahead of the package's
  in your `TEMPLATES` `DIRS`.

## Example / demo project

The repository ships with a runnable demo at [`example/`](./example/)
that wires `siteblog` together with four `django.contrib.sites` rows
(`example.com`, `mac-mini`, `localhost`, `127.0.0.1`) so you can see
per-host filtering in action from a single dev server. The seeded
articles use the `<!-- split -->` marker, so the homepage shows just
the excerpt with a "Read more →" link, while the detail page renders
the full body with `<strong>` / `<em>` / `<h2>` / lists / blockquotes /
`<code>` to illustrate the package's `|safe` rendering path.

Quick start:

```bash
cd example
DJANGO_SETTINGS_MODULE=example_project.settings uv run python manage.py migrate
DJANGO_SETTINGS_MODULE=example_project.settings uv run python manage.py seed_demo
DJANGO_SETTINGS_MODULE=example_project.settings uv run python manage.py createsuperuser
DJANGO_SETTINGS_MODULE=example_project.settings uv run python manage.py runserver
```

Then visit <http://localhost:8000/>. The header shows a **"Sign in to
admin"** link pointing at `/admin/login/`, which switches to **"Admin
(username)"** once you sign in.

### Optional: TinyMCE rich text editor in the admin

The package ships with a plain `<textarea>` for `article_body`. The
example project can swap that for a [TinyMCE](https://www.tiny.cloud/)
editor via the `rich-editor` extras dependency:

```bash
# from the repository root:
uv sync --extra rich-editor                   # installs django-tinymce

cd example
RICH_EDITOR=1 DJANGO_SETTINGS_MODULE=example_project.settings \
    uv run python manage.py runserver
```

When `RICH_EDITOR=1` is set, the example's `settings.py` adds
`tinymce` to `INSTALLED_APPS`, the URLconf mounts `tinymce.urls`, and
`example_project/admin.py` (auto-loaded by Django's admin
autodiscover) unregisters the package's `ArticleAdmin` and
re-registers it with a TinyMCE widget on `article_body`. The model,
migrations, and public view are unchanged — only the admin form
widget differs, so the rich editor is purely a demo-side overlay you
can opt into in your own project.

If `RICH_EDITOR=1` is set but `django-tinymce` is missing,
`settings.py` raises a clear `ImproperlyConfigured` at startup with
the exact install command, instead of a `ModuleNotFoundError` from
deep in Django's app registry.

See [`example/README.md`](./example/README.md) for the multi-host
testing recipe (`/etc/hosts` vs. `curl --resolve`) and a full
breakdown of which articles are visible on which hostnames.

## Development

```bash
git clone https://github.com/iplweb/django-site-blog.git
cd django-site-blog
uv sync --all-extras
DJANGO_SETTINGS_MODULE=tests.settings uv run pytest
```

`pre-commit install` to wire ruff + pyupgrade + django-upgrade.

## License

MIT — see [LICENSE](./LICENSE).
