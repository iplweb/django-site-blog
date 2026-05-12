# django-miniblog

Small Django blog / news app with multi-site support
(`django.contrib.sites`).

Lets editors restrict an article to one or more `Site` objects, or
leave the assignment empty so the article appears on every site that
runs the same Django project.

## Installation

```bash
pip install django-miniblog
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

## Requirements

- Python ≥ 3.10
- Django ≥ 5.2 (tested against 5.2 LTS and 6.0)
- [django-model-utils](https://pypi.org/project/django-model-utils/)
  ≥ 4.5 (for `SplitField`, `TimeStampedModel`, `StatusModel`)

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
git clone https://github.com/<owner>/django-miniblog.git
cd django-miniblog
uv sync --all-extras
DJANGO_SETTINGS_MODULE=tests.settings uv run pytest
```

`pre-commit install` to wire ruff + pyupgrade + django-upgrade.

## License

MIT — see [LICENSE](./LICENSE).
