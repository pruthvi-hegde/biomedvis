from django.urls import path

from .views import article
from .views.filterscreen import CategoryList

urlpatterns = [
    path('category-list', CategoryList.as_view(), name="category-list"),
    path('', article.article_list, name='article-list'),
    path('articles-search', article.populate_on_search, name='search'),
    path('filter-data', article.filter_data, name='app'),
    path('embedding-view', article.create_embedding_view, name='embedding'),
    path('update-article-view', article.update_article_view_from_lasso_box_select, name='update-article-view'),
    path('update-article-time-view', article.update_article_view_from_time_chart, name='update-article-time'),
    path('populate-details-view', article.populate_details_view, name='populate-details-view')
]
