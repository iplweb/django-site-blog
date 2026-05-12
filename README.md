# django-sites-blog

[![Tests](https://github.com/iplweb/django-sites-blog/actions/workflows/tests.yml/badge.svg)](https://github.com/iplweb/django-sites-blog/actions/workflows/tests.yml)
[![Python](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13%20%7C%203.14-blue)](https://github.com/iplweb/django-sites-blog)
[![Django](https://img.shields.io/badge/django-5.2%20LTS%20%7C%206.0-0c4b33)](https://github.com/iplweb/django-sites-blog)
[![License](https://img.shields.io/github/license/iplweb/django-sites-blog)](LICENSE)

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

`django-sites-blog` keeps one article store and lets editors say, per
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
≥ 4.5 (for `SplitField`, `TimeStampedModel`, `StatusModel`).

## Installation

```bash
uv add django-sites-blog
```

or with pip:

```bash
pip install django-sites-blog
```

Add the app and `django.contrib.sites` to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    "django.contrib.sites",
    "miniblog",
]

SITE_ID = 1  # required by django.contrib.sites
```

Include the URLs in your project's `urls.py`:

```python
urlpatterns = [
    # ...
    path("articles/", include("miniblog.urls")),
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

- `miniblog/article_detail.html` — uses `{% extends "miniblog/base.html" %}`.
- `miniblog/base.html` — a bare HTML skeleton; override it in your
  project by placing a `miniblog/base.html` ahead of the package's
  in your `TEMPLATES` `DIRS`.

## Development

```bash
git clone https://github.com/iplweb/django-sites-blog.git
cd django-sites-blog
uv sync --all-extras
DJANGO_SETTINGS_MODULE=tests.settings uv run pytest
```

`pre-commit install` to wire ruff + pyupgrade + django-upgrade.

## License

MIT — see [LICENSE](./LICENSE).
