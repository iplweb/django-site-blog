from django.conf import settings
from django.db.models import Q
from django.views.generic import DetailView

from .models import Article


class ArticleDetailView(DetailView):
    model = Article
    template_name = "miniblog/article_detail.html"
    context_object_name = "article"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        qs = Article.objects.filter(status=Article.STATUS.published)
        site_id = getattr(settings, "SITE_ID", None)
        if site_id is not None:
            qs = qs.filter(Q(sites__isnull=True) | Q(sites__id=site_id)).distinct()
        return qs
