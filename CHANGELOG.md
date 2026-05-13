# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-05-13

### Added

- Runnable end-to-end demo at `example/`. Seeds four `Site` rows
  (`example.com`, `mac-mini`, plus `localhost` and `127.0.0.1` so the
  demo works zero-config), a `HomeListView` rendering excerpts with a
  "Read more" link gated on `article_body.has_more`, and an admin
  sign-in link in the homepage header.
- Demo articles use the `<!-- split -->` marker on its own line so the
  list view shows the excerpt and the detail view shows the full body
  (`<strong>`, `<em>`, `<h2>`, `<ul>`, `<a>`, `<code>`,
  `<blockquote>`).
- Optional `rich-editor` extras dependency (django-tinymce). Setting
  `RICH_EDITOR=1` in the example's environment swaps the plain admin
  textarea for a TinyMCE widget on `article_body` via an
  `admin.site.unregister` / re-register in
  `example_project/admin.py`. The package model and migrations are
  untouched.
- `example_project/settings.py` probes for `tinymce` before adding it
  to `INSTALLED_APPS` and raises `ImproperlyConfigured` with the exact
  install command if `RICH_EDITOR=1` is set without the extra
  installed, instead of a deep `ModuleNotFoundError` from Django's
  app registry.

### Changed

- `ArticleDetailView` now resolves the active `Site` via
  `django.contrib.sites.shortcuts.get_current_site(request)` instead
  of reading `settings.SITE_ID` directly. Honors `request.site` set by
  `CurrentSiteMiddleware` for per-Host multi-site deployments;
  transparently falls back to `settings.SITE_ID` for single-site
  setups.
- Author-only tooling (`pre-commit`, `ruff`, `pytest`,
  `pytest-django`) moved from `[project.optional-dependencies]` to
  `[dependency-groups]` (PEP 735, uv ≥ 0.4). The user-facing
  `rich-editor` opt-in stays under `[project.optional-dependencies]`.
  CI now installs groups targeted (`--group test`, `--group dev`).
- `django-model-utils` requirement narrowed to `>=5,<6`. The previous
  `>=4.5` was effectively wrong on 5.x because the shipped migration
  raised `TypeError` at load time.

### Fixed

- `0001_initial` is no longer broken on `django-model-utils >= 5`. The
  4.x-only `SplitField(no_excerpt_field=True)` kwarg was removed; the
  migration now uses `SeparateDatabaseAndState` so that the auto-injected
  `_article_body_excerpt` column appears in the migration state without
  being emitted twice in `CREATE TABLE`.

## [0.1.0] - 2026-05-13

### Added

- Initial extraction from
  [iplweb/bpp](https://github.com/iplweb/bpp) @ `85bca5785`.
- `Article.sites` ManyToManyField to `django.contrib.sites.models.Site`.
  Empty M2M means "visible everywhere"; populated M2M restricts visibility.
- `ArticleDetailView` (slug-based, filters by `SITE_ID`).
- `siteblog` URL namespace with `article-detail` route.
- Single squashed `0001_initial` migration for the `Article` model,
  capturing every field (including the `model_utils.SplitField`
  excerpt column `_article_body_excerpt`), the `sites` M2M, and the
  explicit `objects` / `on_site` managers in one shot. Earlier history
  in `iplweb/bpp` had four incremental migrations; collapsing them
  here is intentional because this is the package's first standalone
  release, so there is no downstream migration graph to preserve.
- `BigAutoField` as the package-pinned `default_auto_field`
  (via `SiteblogConfig.default_auto_field`) so the schema stays
  consistent regardless of the consuming project's
  `DEFAULT_AUTO_FIELD` setting.
- Minimal template scaffolding (`article_detail.html`, `base.html`).
- Admin `filter_horizontal` + `list_filter` for the `sites` field.

### Notes for downstream projects upgrading from `miniblog` (`django-sites-blog`)

This is a breaking rename. A project that already had the old
`miniblog` app installed needs to handle the transition on its own
side, before installing `django-site-blog`:

- Drop the `miniblog_article` and `miniblog_article_sites` tables
  (after archiving content if needed).
- `DELETE FROM django_migrations WHERE app = 'miniblog';`
- `DELETE FROM django_content_type WHERE app_label = 'miniblog';`
- Then install `django-site-blog`, set `INSTALLED_APPS = [..., "siteblog"]`,
  and run `migrate` so the new `0001_initial` builds the
  `siteblog_article` schema.

If preserving article content matters, copy rows from `miniblog_article`
into `siteblog_article` after the new migration runs. The schemas are
compatible field-for-field except for `id` (was `AutoField`, now
`BigAutoField`) — that's safe for `INSERT ... SELECT id, ...`.

### Removed

- Hard dependency on the bpp project (`bpp.models.struktura.Uczelnia`).
- `post_save` signal invalidating `bpp.views.browse` cache —
  consumers can attach their own receiver if needed.
