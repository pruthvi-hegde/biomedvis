from django.urls import re_path as url

from django.urls import path
from django.urls import path

from .views import article
from .views.filterscreen import CategoryList

urlpatterns = [
    path('', CategoryList.as_view(), name="category-list"),
    path('article-list', article.article_list, name='article-list'),
    path('filter-data', article.filter_data, name='filter-list')
]
