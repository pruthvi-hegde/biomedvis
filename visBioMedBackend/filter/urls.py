from django.urls import re_path as url

from django.urls import path
from django.urls import path

from .views.filterscreen import CategoryList

urlpatterns = [
    path('', CategoryList.as_view())
]
