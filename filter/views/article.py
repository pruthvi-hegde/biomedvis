import ast
import json

from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from plotly.offline import plot

from ..apps import FiltersConfig
from ..doc_to_vec import calculate_doc_average_word2vec
from ..models.article import Article
from ..models.category import Category, Subcategory

filter_model = FiltersConfig.model


# Article List
def article_list(request):
    url_parameter = request.GET.get("q")

    # If there is a search then below part should execute.
    if url_parameter:
        main_articles = Article.objects.none()

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

    # results = sync_to_async(process_for_embedding_view(articles))
    # This part is to fetch all categories and subcategories rom categories model.
    categories = Category.get_all_categories()

    categories_data = {}
    for cat in categories:
        categories_name = cat.category_name.replace(" ", "_")
        categories_data[categories_name] = Subcategory.objects.filter(category__exact=cat)

    article_title = [article.article_title for article in articles]

    # This is for search
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            template_name="article_cards.html",
            context={'data': articles, 'article_title': article_title}
        )

        data_dict = {"html_from_view": html}

        return JsonResponse(data=data_dict, safe=False)

    # This part is for time filter.
    total_data = Article.objects.count()
    published_date_data = list(Article.objects
                               .values('published_date')
                               .annotate(dcount=Count('published_date'))
                               .order_by()
                               )

    published_date = list(d['published_date'] for d in published_date_data)
    article_count = list(d['dcount'] for d in published_date_data)

    # This should execute for all
    return render(request, 'article_list.html',
                  {
                      'data': articles,
                      'article_title': article_title,
                      'total_data': total_data,
                      'view_item': categories_data,
                      'published_date_data': published_date_data,
                      'published_date': published_date,
                      'article_count': article_count

                  })


# filter data
def filter_data(request):
    species = request.GET.getlist('Species[]')
    scale = request.GET.getlist('Scale[]')
    organ_system = request.GET.getlist('Organ_System[]')
    organ = request.GET.getlist('Organ[]')
    data_source = request.GET.getlist('Data_Source[]')


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
    if organ or data_source:
        if organ:
            print(Article.objects.filter(abstract__icontains='Liver'))
            for org in organ:
                main_articles |= Article.objects.filter(abstract__icontains=org)
                print(main_articles)
        if data_source:
            for ds in data_source:
                main_articles |= Article.objects.filter(publisher__icontains=ds)
    else:
        main_articles = Article.objects.all().order_by('-id')

    article_title = [article.article_title for article in main_articles]
    t = render_to_string('article_cards.html', {'data': main_articles, 'article_title': article_title})
    return JsonResponse({'data': t}, safe=False)


@csrf_exempt
def create_embedding_view(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        response = json.loads(request.body)
        article_titles = ast.literal_eval(response)
        try:
            fig = calculate_doc_average_word2vec(filter_model, article_titles)
            graphs = fig

            t = plot({'data': graphs},
                     output_type='div')

            return JsonResponse({'data': t}, safe=True)
        except RuntimeError as e:
            print("here",e)

    else:
        print("Error occured")
