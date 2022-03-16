from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from ..models.article import Article
from ..models.category import Category, Subcategory


# Article List
def article_list(request):
    url_parameter = request.GET.get("q")
    # url_parameter = url_parameter.split(" ")

    if url_parameter:
        main_articles = Article.objects.none()
        print(main_articles)

        # for query_word in url_parameter:
        #     main_articles |= Article.objects.filter(article_title__icontains=query_word)
        #
        # articles = main_articles
        articles = Article.objects.filter(article_title__icontains=url_parameter)
        if list(articles) == list(main_articles):
            url_parameter = url_parameter.split(" ")
            for query_word in url_parameter:
                main_articles |= Article.objects.filter(article_title__icontains=query_word)

            articles = main_articles

    elif not url_parameter:
        articles = Article.objects.all().order_by('-id')
    else:
        articles = Article.objects.all().order_by('-id')

    total_data = Article.objects.count()

    categories = Category.get_all_categories()

    categories_data = {}
    for cat in categories:
        categories_name = cat.category_name.replace(" ", "_")
        categories_data[categories_name] = Subcategory.objects.filter(category__exact=cat)

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


# filter data
def filter_data(request):
    categories = Category.get_all_categories()
    species = request.GET.getlist('Species[]')
    scale = request.GET.getlist('Scale[]')
    organ_system = request.GET.getlist('Organ_System[]')
    organ = request.GET.getlist('Organ[]')

    # categories = request.GET.getlist('category[]')
    # brands = request.GET.getlist('brand[]')
    # sizes = request.GET.getlist('size[]')
    # minPrice = request.GET['minPrice']
    # maxPrice = request.GET['maxPrice']
    # allProducts = Product.objects.all().order_by('-id').distinct()
    # allProducts = allProducts.filter(productattribute__price__gte=minPrice)
    # allProducts = allProducts.filter(productattribute__price__lte=maxPrice)
    # if len(colors) > 0:
    #     allProducts = allProducts.filter(productattribute__color__id__in=colors).distinct()
    # if len(categories) > 0:
    #     allProducts = allProducts.filter(category__id__in=categories).distinct()
    # if len(brands) > 0:
    #     allProducts = allProducts.filter(brand__id__in=brands).distinct()
    # if len(sizes) > 0:
    #     allProducts = allProducts.filter(productattribute__size__id__in=sizes).distinct()
    # articles = Article.objects.all().order_by('-id')

    # This line needs to be fixed
    main_articles = Article.objects.none()
    for org in organ:
        main_articles |= Article.objects.filter(article_title__icontains=org)

    t = render_to_string('article_cards.html', {'data': main_articles})
    return JsonResponse({'data': t}, safe=False)
