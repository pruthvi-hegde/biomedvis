from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from ..models.article import Article
from ..models.category import Category, Subcategory


# Article List
def article_list(request):
    url_parameter = request.GET.get("q")

    if url_parameter:
        articles = Article.objects.filter(article_title__icontains=url_parameter)
    else:
        articles = Article.objects.all().order_by('-id')

    total_data = Article.objects.count()

    categories = Category.get_all_categories()

    categories_data = {}
    for cat in categories:
        categories_data[cat] = Subcategory.objects.filter(category__exact=cat)

    if request.is_ajax():
        html = render_to_string(
            template_name="article_cards.html",
            context={'data': articles}
        )

        data_dict = {"html_from_view": html}

        return JsonResponse(data=data_dict, safe=False)

    return render(request, 'article_list.html',
                  {
                      'data': articles,
                      'total_data': total_data,
                      'view_item': categories_data
                  })
