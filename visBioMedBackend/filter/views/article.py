from django.shortcuts import render
from django.views.generic.list import ListView
from ..models.article import Article
from ..models.category import Category, Subcategory


#Article List
def article_list(request):
    total_data = Article.objects.count()
    data = Article.objects.all().order_by('-id')
    categories = Category.get_all_categories()

    categories_data = {}
    for cat in categories:
        categories_data[cat] = Subcategory.objects.filter(category__exact=cat)

    return render(request, 'article_list.html',
            {
                          'data': data,
                          'total_data': total_data,
                          'view_item': categories_data
            })


