import pytest
from django.contrib.sites.models import Site

from miniblog.models import Article


@pytest.mark.django_db
def test_detail_view_returns_published_article(client):
    Article.objects.create(
        title="Hello",
        status="published",
        slug="hello",
        article_body="body",
    )
    response = client.get("/hello/")
    assert response.status_code == 200
    assert b"Hello" in response.content


@pytest.mark.django_db
def test_detail_view_excludes_drafts(client):
    Article.objects.create(
        title="Draft", status="draft", slug="draft", article_body="body"
    )
    assert client.get("/draft/").status_code == 404


@pytest.mark.django_db
def test_detail_view_visible_on_assigned_site(client, settings):
    site_one, _ = Site.objects.get_or_create(domain="one.example.com", name="One")
    settings.SITE_ID = site_one.id

    article = Article.objects.create(
        title="One",
        status="published",
        slug="one",
        article_body="body",
    )
    article.sites.add(site_one)

    assert client.get("/one/").status_code == 200


@pytest.mark.django_db
def test_detail_view_hidden_on_other_site(client, settings):
    site_one, _ = Site.objects.get_or_create(domain="one.example.com", name="One")
    site_two, _ = Site.objects.get_or_create(domain="two.example.com", name="Two")
    settings.SITE_ID = site_two.id

    article = Article.objects.create(
        title="One only",
        status="published",
        slug="one-only",
        article_body="body",
    )
    article.sites.add(site_one)

    assert client.get("/one-only/").status_code == 404


@pytest.mark.django_db
def test_detail_view_visible_everywhere_when_no_sites(client, settings):
    site_one, _ = Site.objects.get_or_create(domain="one.example.com", name="One")
    site_two, _ = Site.objects.get_or_create(domain="two.example.com", name="Two")

    Article.objects.create(
        title="Global",
        status="published",
        slug="global",
        article_body="body",
    )

    settings.SITE_ID = site_one.id
    assert client.get("/global/").status_code == 200

    settings.SITE_ID = site_two.id
    assert client.get("/global/").status_code == 200
