import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse


@pytest.fixture
def admin_client(db):
    User = get_user_model()
    User.objects.create_superuser("admin", "admin@example.com", "pw")
    c = Client()
    c.login(username="admin", password="pw")
    return c


@pytest.mark.django_db
def test_article_admin_changelist(admin_client):
    url = reverse("admin:siteblog_article_changelist")
    response = admin_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_article_admin_add_view(admin_client):
    url = reverse("admin:siteblog_article_add")
    response = admin_client.get(url)
    assert response.status_code == 200
