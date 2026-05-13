from django.urls import path

from .views import ArticleDetailView

app_name = "siteblog"

urlpatterns = [
    path("<slug:slug>/", ArticleDetailView.as_view(), name="article-detail"),
]
