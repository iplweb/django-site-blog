# Example project for `django-site-blog`

Bare-minimum Django project that installs `siteblog` and exposes its
URLs at `/articles/`.

```bash
cd example
DJANGO_SETTINGS_MODULE=example_project.settings uv run python manage.py migrate
DJANGO_SETTINGS_MODULE=example_project.settings uv run python manage.py createsuperuser
DJANGO_SETTINGS_MODULE=example_project.settings uv run python manage.py runserver
```

Then:

- visit <http://127.0.0.1:8000/admin/> to log in and create an `Article`,
- pick which `Sites` it should appear on (leave empty for "every site"),
- visit <http://127.0.0.1:8000/articles/your-slug/> to view it.

`SITE_ID` is hard-coded to `1` in `example_project/settings.py`. Add
more rows to `django.contrib.sites.Site` in the admin and bump
`SITE_ID` (or wire `django.contrib.sites.middleware.CurrentSiteMiddleware`
properly) to see the per-site filtering in action.
