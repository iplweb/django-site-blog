from django.contrib.sites.shortcuts import get_current_site
from django.views.generic import ListView

from siteblog.models import Article


class HomeListView(ListView):
    template_name = "example_project/home.html"
    context_object_name = "articles"

    def get_queryset(self):
        site = get_current_site(self.request)
        return Article.objects.published().visible_on_site(site)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["current_site"] = get_current_site(self.request)
        return ctx
