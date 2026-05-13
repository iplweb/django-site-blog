# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- `0001_initial` is no longer broken on `django-model-utils >= 5`. The
  4.x-only `SplitField(no_excerpt_field=True)` kwarg was removed; the
  migration now uses `SeparateDatabaseAndState` so that the auto-injected
  `_article_body_excerpt` column appears in the migration state without
  being emitted twice in `CREATE TABLE`.

### Changed

- `django-model-utils` requirement narrowed to `>=5,<6`. The previous
  `>=4.5` was effectively wrong on 5.x because the shipped migration
  raised `TypeError` at load time.

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
