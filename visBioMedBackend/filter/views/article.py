from django.shortcuts import render
from django.views.generic.list import ListView
from ..models.article import Article
from ..models.category import Category, Subcategory


#Article List
def article_list(request):
    total_data = Article.objects.count()
    data = Article.objects.all().order_by('-id')[:3]
    return render(request, 'article_list.html',
            {
                          'data': data,
                          'total_data': total_data
            })


def filter_data(request):
    categories = Category.objects.all()
    return render(request, 'filter.html', categories)
