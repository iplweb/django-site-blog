from django.contrib.sites.shortcuts import get_current_site
from django.views.generic import DetailView

from .models import Article


class ArticleDetailView(DetailView):
    model = Article
    template_name = "siteblog/article_detail.html"
    context_object_name = "article"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        # get_current_site honors request.site (set by CurrentSiteMiddleware
        # from the Host header) and falls back to settings.SITE_ID, so the
        # same view works for single-site and per-host multi-site deployments.
        site = get_current_site(self.request)
        return Article.objects.published().visible_on_site(site)
