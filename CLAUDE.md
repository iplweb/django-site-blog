# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Package vs. app name mismatch (read this first)

The PyPI distribution is **`django-site-blog`** but the actual Django app — the Python package, the app label, the URL namespace, the migration `app_label`, the template directory, the admin reverse names — is all **`siteblog`**. Examples:

- Source lives at `src/siteblog/`, not `src/django_site_blog/`.
- `INSTALLED_APPS = ["siteblog"]` (see `tests/settings.py:22`, `example/example_project/settings.py:19`).
- URL namespace: `app_name = "siteblog"` (`src/siteblog/urls.py:5`); reverse via `siteblog:article-detail`.
- Admin reverse: `admin:siteblog_article_change` / `admin:siteblog_article_changelist`.
- Migrations live under `src/siteblog/migrations/` with `app_label="siteblog"`.
- `pyproject.toml` ships package data under `siteblog = [...]`.

Do **not** rename `siteblog` to `django_site_blog` casually — it would require renaming migrations, every reverse string, the URL namespace, and a migration that rewrites `app_label`. If a rename is on the table, treat it as a dedicated piece of work.

The package was previously named `miniblog` (PyPI: `django-sites-blog`). The rename happened in 2026-05; the migration files and table names switched from the `miniblog` to the `siteblog` app label as part of that change. Downstream installs that were on the old name need to `UPDATE django_migrations SET app='siteblog' WHERE app='miniblog';`, the same for `django_content_type.app_label`, and rename the `miniblog_article` table to `siteblog_article` before re-running migrations.

## Architecture (the big picture)

Single-model reusable Django app. The whole package is one model (`Article`), one view (`ArticleDetailView`), one admin, two templates, four migrations.

### Sites-scoping model — the headline feature

`Article.sites` is an M2M to `django.contrib.sites.models.Site` with **inverted-default semantics**:

- **Empty M2M ⇒ article is visible on every site.**
- **Non-empty M2M ⇒ article is restricted to the listed sites.**

This is enforced in `ArticleDetailView.get_queryset` (`src/siteblog/views.py:15-20`) with a single OR query:

```python
qs.filter(Q(sites__isnull=True) | Q(sites__id=site_id)).distinct()
```

**`Article.on_site` exists but does NOT implement these semantics.** It is a standard `CurrentSiteManager("sites")` and treats empty-M2M articles as invisible everywhere. Two managers coexist on the model on purpose:

- `Article.objects` — the OR-default manager-less query used by the view.
- `Article.on_site` — pure current-site-only (no empty-equals-all fallback).

If a future change adds a list view, decide which semantics it should follow and document the choice. Don't silently switch the detail view to `on_site` — it would break the empty-M2M default.

### Status, URLs, content

- Status comes from `model_utils.StatusModel` with `Choices(("draft", _("draft")), ("published", _("published")))`. The view filters to `status="published"`; drafts 404 on the public URL.
- `get_absolute_url()` is mode-aware: drafts return the admin change URL, published articles return the public detail URL (`src/siteblog/models.py:52-55`). Keep this dual behaviour if you touch it — tests at `tests/test_models.py:22-37` lock it in.
- `article_body` is a `model_utils.fields.SplitField`. The split marker comes from `settings.SPLIT_MARKER` (default `"<!-- split -->"`), exposed for the admin help text only — actual splitting is `model_utils`' responsibility.
- `article_body.content` is rendered with `|safe` in `templates/siteblog/article_detail.html:15`. Authors enter HTML directly; there is no sanitisation layer.

### Quirks worth knowing

- `Article.__str__` returns the Polish literal `f'Artykuł "{title}" - {status_label}"'` (`src/siteblog/models.py:58`). The status label is translated; the surrounding word is not. Inherited from the upstream `bpp` extraction — `tests/test_models.py:8-18` accepts both Polish and English labels.
- Polish translations ship at `src/siteblog/locale/pl/LC_MESSAGES/`.
- The project descends from `iplweb/bpp @ 85bca5785` (see `CHANGELOG.md`). The hard dependency on `bpp.models.struktura.Uczelnia` and the `post_save` cache-invalidation signal were removed during extraction.

## Common commands

The project is `uv`-managed; CI uses uv exclusively.

```bash
uv sync --all-extras --all-groups                          # full local install (incl. rich-editor extra + dev/test groups)
DJANGO_SETTINGS_MODULE=tests.settings uv run pytest        # full test suite
uv run pytest tests/test_views.py::test_detail_view_hidden_on_other_site  # one test
uv run ruff check .                                        # lint
uv run ruff format --check .                               # format check (CI uses this)
uv run ruff format .                                       # apply formatting
pre-commit install                                         # one-time, then runs on commit
pre-commit run --all-files                                 # manual full pass
```

Dependency layout (PEP 735):

- `[project.optional-dependencies]` — **user-facing extras**, published in PyPI metadata. Currently: `rich-editor` (django-tinymce) for the example demo's optional admin widget.
- `[dependency-groups]` — **author-only tooling**, never published. `test` (pytest, pytest-django) and `dev` (pre-commit, ruff). CI installs them targeted: `uv sync --group test` for the test matrix and `uv sync --group dev` for lint.

Running the example project (a real Django project that depends on the in-tree app):

```bash
cd example
DJANGO_SETTINGS_MODULE=example_project.settings uv run python manage.py migrate
DJANGO_SETTINGS_MODULE=example_project.settings uv run python manage.py createsuperuser
DJANGO_SETTINGS_MODULE=example_project.settings uv run python manage.py runserver
```

There are **two distinct Django settings modules** — don't conflate them:

- `tests.settings` — in-memory sqlite, no CSRF middleware, used by pytest.
- `example_project.settings` — on-disk sqlite at `example/db.sqlite3`, `DEBUG=True`, used by the runnable demo.

## Test layout

- `tests/conftest.py` sets `DJANGO_SETTINGS_MODULE=tests.settings`.
- `tests/urls.py` is the ROOT_URLCONF for tests: admin at `/admin/` + siteblog mounted at root (so detail URLs are `/{slug}/`, see `tests/test_views.py`).
- `tests/settings.py:5` hardcodes `SITE_ID=1`. The sites-scoping tests in `test_views.py` override it per-test via the pytest-django `settings` fixture; do the same when adding scoping tests.
- The default `Site(id=1)` row is created implicitly by the `sites` app's `post_migrate` signal — tests rely on this rather than creating it explicitly.

## Supported Django × Python matrix

CI (`.github/workflows/tests.yml`) tests:

- Django 5.2 LTS × Python 3.10 / 3.11 / 3.12 / 3.13 / 3.14
- Django 6.0 × Python 3.12 / 3.13 / 3.14

`pyproject.toml` requires `django>=5.2`. Pre-commit pins `django-upgrade --target-version 5.2`, so anything that auto-rewrites to Django 5.2-only idioms is expected and fine.

## Migrations

There is exactly one migration: `0001_initial.py`. It was regenerated from scratch at rename time (the four-migration history inherited from `iplweb/bpp` was discarded because this is the package's first standalone release, so there is no downstream migration graph to preserve). `0001_initial` captures every field on `Article`, including the `_article_body_excerpt` column that `model_utils.fields.SplitField` requires, the `sites` M2M, and the explicit `objects` / `on_site` managers in one `CreateModel`.

`SiteblogConfig.default_auto_field = "django.db.models.BigAutoField"` is the **package's** pin, so the schema stays consistent regardless of what the consuming project sets for `DEFAULT_AUTO_FIELD`.

## django-model-utils pin (this matters)

`pyproject.toml` requires `django-model-utils>=5,<6`. In 5.x, `SplitField.deconstruct()` no longer accepts the 4.x-only `no_excerpt_field=True` opt-out, so `contribute_to_class` always auto-injects an `_<name>_excerpt` `TextField` at runtime. If the migration ALSO declares `_article_body_excerpt` explicitly in `CreateModel.fields`, the SchemaEditor emits the column twice and `migrate` dies with `duplicate column name: _article_body_excerpt`.

The fix in `0001_initial.py` is `migrations.SeparateDatabaseAndState`:

- The `database_operations` `CreateModel` lists only the explicit fields (no excerpt). The SchemaEditor reifies the live model class — which has the auto-injected excerpt column — so the resulting `CREATE TABLE` includes `_article_body_excerpt` exactly once.
- The `state_operations` `CreateModel` lists the explicit fields **plus** `_article_body_excerpt` so the migration graph state knows the column exists. Without this, `makemigrations` keeps proposing spurious `AddField` operations on every run.

Do not lift the `<6` ceiling on `django-model-utils` without re-validating this dance — a future major could change the auto-injection semantics again.

## Queryset API (centralized site filter)

`Article.objects` is an `ArticleQuerySet.as_manager()`. Chain `.published()` and `.visible_on_site(site)` to centralize the inverted-M2M visibility query — see `src/siteblog/views.py` for the canonical usage. `visible_on_site` accepts a `Site` instance or its primary key. **Do not bypass it with `Article.on_site`** for list/detail views: `on_site` is a plain `CurrentSiteManager` and drops empty-M2M ("visible everywhere") articles.

Note: `as_manager()` produces a synthetic Manager class with no stable import path, so Django's migration serializer renders it as plain `django.db.models.manager.Manager()` in `0001_initial`'s `MANAGERS` list. That's expected — the runtime QuerySet methods come from the live model class, not the migration record. `makemigrations --check` stays green.
