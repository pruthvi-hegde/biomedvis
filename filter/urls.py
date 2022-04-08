from django.urls import path

from .views import article
from .views.filterscreen import CategoryList

urlpatterns = [
    path('category-list', CategoryList.as_view(), name="category-list"),
    path('', article.article_list, name='article-list'),
    path('articles-search', article.article_list, name='search'),
    path('filter-data', article.filter_data, name='filter'),
    path('embedding_view', article.create_embedding_view, name='embedding')
]
