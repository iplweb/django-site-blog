import pytest
from django.contrib.sites.models import Site
from django.db import IntegrityError

from miniblog.models import Article


def test_article_str():
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
def test_get_absolute_url_draft():
    article = Article.objects.create(
        title="Draft", status="draft", slug="draft", article_body="body"
    )
    url = article.get_absolute_url()
    assert "admin" in url
    assert "miniblog" in url
    assert str(article.pk) in url


@pytest.mark.django_db
def test_get_absolute_url_published():
    article = Article.objects.create(
        title="Pub", status="published", slug="pub", article_body="body"
    )
    assert article.get_absolute_url() == "/pub/"


@pytest.mark.django_db
def test_slug_uniqueness():
    Article.objects.create(title="A", slug="dup", article_body="b1")
    with pytest.raises(IntegrityError):
        Article.objects.create(title="B", slug="dup", article_body="b2")


@pytest.mark.django_db
def test_ordering_by_published_on_desc_then_title():
    from datetime import timedelta

    from django.utils import timezone

    now = timezone.now()
    older = Article.objects.create(
        title="Older",
        slug="older",
        article_body="b",
        published_on=now - timedelta(days=2),
    )
    middle = Article.objects.create(
        title="Middle",
        slug="middle",
        article_body="b",
        published_on=now - timedelta(days=1),
    )
    newest = Article.objects.create(
        title="Newest", slug="newest", article_body="b", published_on=now
    )

    assert list(Article.objects.all()) == [newest, middle, older]


@pytest.mark.django_db
def test_status_choices():
    assert "draft" in Article.STATUS
    assert "published" in Article.STATUS
    assert len(Article.STATUS) == 2


@pytest.mark.django_db
def test_article_with_no_sites_has_empty_m2m():
    article = Article.objects.create(
        title="Global", status="published", slug="global", article_body="b"
    )
    assert article.sites.count() == 0


@pytest.mark.django_db
def test_article_assigned_to_specific_sites():
    site_one, _ = Site.objects.get_or_create(domain="one.example.com", name="One")
    site_two, _ = Site.objects.get_or_create(domain="two.example.com", name="Two")

    article = Article.objects.create(
        title="A", status="published", slug="a", article_body="b"
    )
    article.sites.add(site_one)

    assert list(article.sites.all()) == [site_one]
    assert site_two not in article.sites.all()
