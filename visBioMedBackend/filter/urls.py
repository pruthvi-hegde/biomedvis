from django.urls import re_path as url

from django.urls import path
from django.urls import path

from .views import article
from .views.filterscreen import CategoryList

urlpatterns = [
    path('category-list', CategoryList.as_view(), name="category-list"),
    path('', article.article_list, name='article-list')
]
