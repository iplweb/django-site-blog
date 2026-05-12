from django.urls import path

from .views import ArticleDetailView

app_name = "miniblog"

urlpatterns = [
    path("<slug:slug>/", ArticleDetailView.as_view(), name="article-detail"),
]
