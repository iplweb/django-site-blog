# Example project for `django-site-blog`

A runnable Django project that wires up `siteblog` together with two
`django.contrib.sites` rows so you can see per-host filtering in action
from a single dev server.

## What the demo shows

`Article.sites` is a many-to-many to `Site` with **inverted-default**
semantics:

- empty M2M ⇒ article is visible on every site;
- non-empty M2M ⇒ article is restricted to the listed sites only.

The seed command creates four `Site` rows (`example.com`, `mac-mini`,
plus `localhost` and `127.0.0.1` so the demo "just works" without
`/etc/hosts` edits) and a handful of articles spread across:

- visible everywhere (no site selected),
- visible on `example.com` only,
- visible on `mac-mini` only,
- a draft (never public, regardless of site).

The seeded articles use the `<!-- split -->` marker, so the homepage
shows just the **excerpt** with a "Read more →" link, while the detail
page renders the full body. Bodies use ordinary HTML (`<strong>`,
`<em>`, `<h2>`, `<ul>`, `<a>`, `<code>`, `<blockquote>`) to illustrate
that `article_body.content|safe` lets authors hand-write markup —
there is no sanitisation layer, so only trusted editors should have
admin access.

`example_project/settings.py` deliberately leaves `SITE_ID` unset, so
`django.contrib.sites.middleware.CurrentSiteMiddleware` picks the
matching `Site` row from the request's `Host:` header on every request.

## Running it

```bash
cd example
DJANGO_SETTINGS_MODULE=example_project.settings uv run python manage.py migrate
DJANGO_SETTINGS_MODULE=example_project.settings uv run python manage.py seed_demo
DJANGO_SETTINGS_MODULE=example_project.settings uv run python manage.py createsuperuser
DJANGO_SETTINGS_MODULE=example_project.settings uv run python manage.py runserver
```

The server listens on `127.0.0.1:8000`. Visiting
<http://127.0.0.1:8000/> or <http://localhost:8000/> works immediately
and shows only the "visible everywhere" articles (those two hosts have
no site-restricted articles assigned).

## Signing in to the admin

The homepage header shows a **"Sign in to admin"** link that points at
`/admin/login/`. After running `createsuperuser` above, you can sign in
there to manage articles. Once authenticated, the same header switches
to **"Admin (your-username)"** and links straight to the admin index.

The admin URL is `/admin/` on every host — for example,
<http://localhost:8000/admin/> or <http://example.com:8000/admin/>.

## Optional: rich text editor in the admin

The package ships with a plain `<textarea>` for `article_body`. The
example project can swap that for a [TinyMCE](https://www.tiny.cloud/)
editor by installing the `rich-editor` extra and setting an env var:

```bash
# from the repository root:
uv sync --extra rich-editor                # installs django-tinymce
# or: uv sync --all-extras

cd example
RICH_EDITOR=1 DJANGO_SETTINGS_MODULE=example_project.settings \
    uv run python manage.py runserver
```

When `RICH_EDITOR=1` is set, `example_project/settings.py` adds
`tinymce` to `INSTALLED_APPS`, the example URLconf mounts
`tinymce.urls` at `/tinymce/`, and `example_project/admin.py`
unregisters the package's `ArticleAdmin` and re-registers it with a
TinyMCE widget on `article_body`. The model, migrations and public
view are unchanged — only the admin form widget differs.

If `RICH_EDITOR=1` is set but `django-tinymce` is missing,
`settings.py` raises an `ImproperlyConfigured` at startup with the
exact install command, rather than letting Django's app registry emit
a `ModuleNotFoundError` deep in the traceback.

Leave `RICH_EDITOR` unset to keep the default plain-textarea
behaviour.

## Multi-host testing (`example.com` / `mac-mini`)

To exercise per-host filtering, reach the demo as `example.com` or
`mac-mini`. Either add them to your `/etc/hosts`:

```
127.0.0.1   example.com mac-mini
```

…then visit <http://example.com:8000/> and <http://mac-mini:8000/>, or
use `curl --resolve` from another terminal:

```bash
curl --resolve example.com:8000:127.0.0.1 http://example.com:8000/
curl --resolve mac-mini:8000:127.0.0.1   http://mac-mini:8000/
```

You should see different article lists for each host. Cross-host
detail URLs (e.g. opening `/mac-mini-only/` while on `example.com`)
return `404`.

`seed_demo` is idempotent — re-run it whenever you want to reset the
demo content.
