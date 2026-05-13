"""Optional admin overrides for the example project.

When ``RICH_EDITOR=1`` is set in the environment (and ``django-tinymce``
is installed), this module unregisters the plain ``ArticleAdmin`` shipped
with the package and re-registers it with a TinyMCE widget on the
``article_body`` field. The model and migrations are unchanged — only
the admin form widget differs.
"""

from django.conf import settings

if settings.RICH_EDITOR:
    from django.contrib import admin

    # Importing the widget here (rather than at module top) keeps the
    # example importable when `django-tinymce` is not installed and the
    # flag is off.
    from tinymce.widgets import TinyMCE

    from siteblog.admin import ArticleAdmin, ArticleForm
    from siteblog.models import Article

    class RichArticleForm(ArticleForm):
        class Meta(ArticleForm.Meta):
            widgets = {
                **ArticleForm.Meta.widgets,
                "article_body": TinyMCE(attrs={"cols": 80, "rows": 20}),
            }

    class RichArticleAdmin(ArticleAdmin):
        form = RichArticleForm

    admin.site.unregister(Article)
    admin.site.register(Article, RichArticleAdmin)
