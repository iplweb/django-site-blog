# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Initial extraction from
  [iplweb/bpp](https://github.com/iplweb/bpp) @ `85bca5785`.
- `Article.sites` ManyToManyField to `django.contrib.sites.models.Site`.
  Empty M2M means "visible everywhere"; populated M2M restricts visibility.
- `ArticleDetailView` (slug-based, filters by `SITE_ID`).
- `miniblog` URL namespace with `article-detail` route.
- Minimal template scaffolding (`article_detail.html`, `base.html`).
- Admin `filter_horizontal` + `list_filter` for the `sites` field.

### Removed

- Hard dependency on the bpp project (`bpp.models.struktura.Uczelnia`).
- `post_save` signal invalidating `bpp.views.browse` cache —
  consumers can attach their own receiver if needed.
