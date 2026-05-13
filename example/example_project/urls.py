from django.conf import settings
from django.contrib import admin
from django.urls import include, path

from example_project.views import HomeListView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeListView.as_view(), name="home"),
    path("", include("siteblog.urls")),
]

if settings.RICH_EDITOR:
    # django-tinymce serves the JS bundle + filebrowser callback from
    # its own URL prefix. Mount it only when the editor is enabled.
    urlpatterns.append(path("tinymce/", include("tinymce.urls")))
