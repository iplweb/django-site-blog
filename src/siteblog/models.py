from django.conf import settings
from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import Q
from django.urls.base import reverse
from django.utils import timezone
from django.utils.html import escape
from django.utils.translation import gettext_lazy as _
from model_utils.choices import Choices
from model_utils.fields import SplitField
from model_utils.models import StatusModel, TimeStampedModel

SPLIT_MARKER = getattr(settings, "SPLIT_MARKER", "<!-- split -->")


class ArticleQuerySet(models.QuerySet):
    def published(self):
        return self.filter(status="published")

    def visible_on_site(self, site):
        # Empty `sites` M2M means "visible everywhere"; otherwise the article
        # is restricted to the listed sites. `site` can be a `Site` instance
        # or a primary-key int.
        site_id = getattr(site, "id", site)
        return self.filter(Q(sites__isnull=True) | Q(sites__id=site_id)).distinct()


class Article(TimeStampedModel, StatusModel):
    STATUS = Choices(("draft", _("draft")), ("published", _("published")))

    title = models.TextField(verbose_name=_("Title"))
    article_body = SplitField(
        verbose_name=_("Article body"),
        help_text=_(
            'Use the split marker "%s" in case you want to display '
            "the shorter version of the article body"
        )
        % escape(SPLIT_MARKER),
    )
    published_on = models.DateTimeField(
        verbose_name=_("Published on"), default=timezone.now
    )
    slug = models.SlugField(unique=True)

    sites = models.ManyToManyField(
        Site,
        blank=True,
        related_name="articles",
        verbose_name=_("Sites"),
        help_text=_(
            "Restrict this article to selected sites. "
            "Leave empty to make it visible on all sites."
        ),
    )

    objects = ArticleQuerySet.as_manager()
    on_site = CurrentSiteManager("sites")

    class Meta:
        verbose_name_plural = _("Articles")
        verbose_name = _("Article")
        ordering = ("-published_on", "title")

    def get_absolute_url(self):
        if self.status != self.STATUS.published:
            return reverse("admin:siteblog_article_change", args=(self.pk,))
        return reverse("siteblog:article-detail", args=(self.slug,))

    def __str__(self):
        return f'Artykuł "{self.title}" - {self.STATUS[self.status]}'
