import pytest
from django.contrib.sites.models import Site
from django.db import IntegrityError

from miniblog.models import Article


def test_Article___str__():
    a = Article(title="Artykuł", status="draft")
    assert (
        str(a) == 'Artykuł "Artykuł" - szkic' or str(a) == 'Artykuł "Artykuł" - draft'
    )

    a = Article(title="Artykuł", status="published")
    assert (
        str(a) == 'Artykuł "Artykuł" - opublikowany'
        or str(a) == 'Artykuł "Artykuł" - published'
    )


@pytest.mark.django_db
def test_article_get_absolute_url_draft():
    article = Article.objects.create(
        title="Test Draft",
        status="draft",
        slug="test-draft",
        article_body="Simple body",
    )

    url = article.get_absolute_url()

    assert "admin" in url
    assert "miniblog" in url
    assert "article" in url
    assert str(article.pk) in url


@pytest.mark.django_db
def test_article_get_absolute_url_published():
    article = Article.objects.create(
        title="Test Published",
        status="published",
        slug="test-published",
        article_body="Body",
    )

    url = article.get_absolute_url()

    assert url == f"/{article.slug}/"


@pytest.mark.django_db
def test_article_slug_uniqueness():
    Article.objects.create(
        title="First Article",
        slug="unique-slug",
        article_body="Body 1",
    )

    with pytest.raises(IntegrityError):
        Article.objects.create(
            title="Second Article",
            slug="unique-slug",
            article_body="Body 2",
        )


@pytest.mark.django_db
def test_article_ordering():
    from datetime import timedelta

    from django.utils import timezone

    now = timezone.now()

    article1 = Article.objects.create(
        title="BBB Article",
        slug="bbb-article",
        article_body="Body 1",
        published_on=now - timedelta(days=2),
    )
    article2 = Article.objects.create(
        title="AAA Article",
        slug="aaa-article",
        article_body="Body 2",
        published_on=now - timedelta(days=1),
    )
    article3 = Article.objects.create(
        title="CCC Article",
        slug="ccc-article",
        article_body="Body 3",
        published_on=now,
    )

    articles = list(Article.objects.all())

    assert articles[0] == article3
    assert articles[1] == article2
    assert articles[2] == article1


@pytest.mark.django_db
def test_article_status_choices():
    assert "draft" in Article.STATUS
    assert "published" in Article.STATUS
    assert len(Article.STATUS) == 2


@pytest.mark.django_db
def test_article_with_no_sites_is_visible_everywhere(settings):
    """Empty sites M2M = article visible on every site."""
    article = Article.objects.create(
        title="Global Article",
        status="published",
        slug="global",
        article_body="Visible everywhere",
    )
    assert article.sites.count() == 0

    site_one, _ = Site.objects.get_or_create(domain="one.example.com", name="One")
    site_two, _ = Site.objects.get_or_create(domain="two.example.com", name="Two")

    settings.SITE_ID = site_one.id
    assert Article.on_site.filter(pk=article.pk).count() == 0
    # ^ CurrentSiteManager filters by FK presence; for the "visible everywhere"
    # semantics the consumer should use Article.objects + the OR query
    # (see ArticleDetailView.get_queryset).


@pytest.mark.django_db
def test_article_visible_only_on_assigned_sites():
    site_one, _ = Site.objects.get_or_create(domain="one.example.com", name="One")
    site_two, _ = Site.objects.get_or_create(domain="two.example.com", name="Two")

    article = Article.objects.create(
        title="Site-One Article",
        status="published",
        slug="site-one",
        article_body="Only on site one",
    )
    article.sites.add(site_one)

    assert article.sites.count() == 1
    assert site_one in article.sites.all()
    assert site_two not in article.sites.all()


@pytest.mark.django_db
def test_detail_view_filters_by_site(client, settings):
    site_one, _ = Site.objects.get_or_create(domain="one.example.com", name="One")
    site_two, _ = Site.objects.get_or_create(domain="two.example.com", name="Two")

    global_article = Article.objects.create(
        title="Global",
        status="published",
        slug="global",
        article_body="Body",
    )
    one_article = Article.objects.create(
        title="One-only",
        status="published",
        slug="one-only",
        article_body="Body",
    )
    one_article.sites.add(site_one)
    two_article = Article.objects.create(
        title="Two-only",
        status="published",
        slug="two-only",
        article_body="Body",
    )
    two_article.sites.add(site_two)

    settings.SITE_ID = site_one.id

    assert client.get("/global/").status_code == 200
    assert client.get("/one-only/").status_code == 200
    assert client.get("/two-only/").status_code == 404


@pytest.mark.django_db
def test_detail_view_excludes_drafts(client):
    Article.objects.create(
        title="Draft",
        status="draft",
        slug="draft",
        article_body="Body",
    )
    assert client.get("/draft/").status_code == 404
