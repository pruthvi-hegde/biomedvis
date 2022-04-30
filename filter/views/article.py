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
    print(url_parameter)

    # If there is a search then below part should execute.
    if url_parameter:
        main_articles = Article.objects.none()

        articles = Article.objects.filter(abstract__icontains=url_parameter)
        if list(articles) == list(main_articles):
            # url_parameter = url_parameter.split(" ")
            # for query_word in url_parameter:
            #     main_articles |= Article.objects.filter(abstract__icontains=query_word)

            articles = main_articles
    elif not url_parameter:
        articles = Article.objects.all().order_by('-id')
    else:
        articles = Article.objects.all().order_by('-id')

    # This part is to fetch all categories and subcategories rom categories model.
    categories = Category.get_all_categories()

    categories_data = {}
    for cat in categories:
        categories_name = cat.category_name.replace(" ", "_")
        categories_data[categories_name] = Subcategory.objects.filter(category__exact=cat)

    article_title, published_date, article_count = get_article_published_year_and_count(articles)

    # This is for search
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string(
            template_name="component_view.html",
            context={'data': articles, 'article_title': article_title, 'published_date': published_date,
                     'article_count': article_count}
        )

        data_dict = {'data': html}

        return JsonResponse(data=data_dict, safe=False)

    # This part is for time filter.
    total_data = Article.objects.count()

    # This should execute for all
    return render(request, 'main.html',
                  {
                      'data': articles,
                      'article_title': article_title,
                      'total_data': total_data,
                      'view_item': categories_data,
                      'published_date': published_date,
                      'article_count': article_count

                  })


def filter_data(request):
    species = request.GET.getlist('Species[]')
    scale = request.GET.getlist('Scale[]')
    organ = request.GET.getlist('Organ[]')
    data_source = request.GET.getlist('Data_Source[]')
    algorithm = request.GET.getlist('Algorithm[]')
    dimension = request.GET.getlist('Dimension[]')

    # This line needs to be fixed
    main_articles = Article.objects.none()

    for org in organ:
        main_articles |= Article.objects.filter(abstract__icontains=org)

    for ds in data_source:
        main_articles |= Article.objects.filter(abstract__icontains=ds)

    for sc in scale:
        main_articles |= Article.objects.filter(abstract__icontains=sc)

    for sp in species:
        main_articles |= Article.objects.filter(abstract__icontains=sp)

    for al in algorithm:
        main_articles |= Article.objects.filter(abstract__icontains=al)

    for dm in dimension:
        main_articles |= Article.objects.filter(abstract__icontains=dm)

    if not organ and not data_source and not scale and not species and not dimension and not algorithm:
        main_articles = Article.objects.all().order_by('-id')

    article_title, published_date, article_count = get_article_published_year_and_count(main_articles)

    t = render_to_string('component_view.html', {'data': main_articles, 'article_title': article_title,
                                                 'published_date': published_date,
                                                 'article_count': article_count
                                                 })
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
            return JsonResponse({'data': t, 'dragmode': 'lasso'}, safe=True)
        except RuntimeError as e:
            print("Runtime error", e)
    else:
        print("Error occured")


@csrf_exempt
def update_article_view(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        selected_article_points = json.loads(request.body)
        main_articles = Article.objects.none()
        for article_point in selected_article_points:
            main_articles |= Article.objects.filter(article_title__exact=article_point)

        article_title, published_date, article_count = get_article_published_year_and_count(main_articles)
        t = render_to_string('article_page_view.html', {'data': main_articles, 'article_title': article_title})
        tt = {'published_data': published_date, 'article_count': article_count}
        return JsonResponse({'data': t, 'data2': tt}, safe=False)


@csrf_exempt
def update_article_view_from_time_chart(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        article_years = json.loads(request.body)

        main_articles = Article.objects.filter(published_date__gte=article_years[0], published_date__lte=article_years[1])

        article_titles, published_date, article_count = get_article_published_year_and_count(main_articles)

        fig = calculate_doc_average_word2vec(filter_model, article_titles)
        graphs = fig
        tt = plot({'data': graphs}, output_type='div')

        t = render_to_string('article_page_view.html', {'data': main_articles})

        return JsonResponse({'data': t, 'data2': tt}, safe=False)


def get_article_published_year_and_count(main_articles):
    article_title = [article.article_title for article in main_articles]
    published_date_data = list(main_articles
                               .values('published_date')
                               .annotate(dcount=Count('published_date'))
                               .order_by()
                               )

    published_date = list(d['published_date'] for d in published_date_data)
    article_count = list(d['dcount'] for d in published_date_data)
    return article_title, published_date, article_count
