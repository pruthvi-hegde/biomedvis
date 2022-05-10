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
import plotly.express as px

filter_model = FiltersConfig.model


# Article List
def article_list(request):
    articles = Article.objects.all().order_by('-id')

    # This part is to fetch all categories and subcategories from categories model.
    categories = Category.get_all_categories()

    categories_data = {}
    for cat in categories:
        categories_name = cat.category_name.replace(" ", "_")
        categories_data[categories_name] = Subcategory.objects.filter(category__exact=cat)

    article_title, published_date, article_count, total_count = get_article_published_year_and_count(articles)

    # This should execute for all
    return render(request, 'main.html',
                  {
                      'data': articles,
                      'article_title': article_title,
                      'total_count': total_count,
                      'view_item': categories_data,
                      'published_date': published_date,
                      'article_count': article_count

                  })


def filter_data(request):
    filter_values = dict(request.GET)
    main_articles = Article.objects.none()
    if len(filter_values) is not 0:
        for categories in filter_values.values():
            for cat in categories:
                main_articles |= Article.objects.filter(abstract__icontains=cat)
    else:
        main_articles = Article.objects.all().order_by('-id')

    article_title, published_date, article_count, total_count = get_article_published_year_and_count(main_articles)

    t = render_to_string('component_view.html', {'data': main_articles, 'article_title': article_title,
                                                 'published_date': published_date,
                                                 'article_count': article_count,
                                                 'total_count': total_count,
                                                 })
    tt = {'published_data': published_date, 'article_count': article_count, 'total_count': total_count,
          'article_title': article_title}
    return JsonResponse({'data': t, 'data2': tt}, safe=False)


@csrf_exempt
def create_embedding_view(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        response = json.loads(request.body)
        article_titles = ast.literal_eval(response)
        if len(article_titles) != 1:
            try:
                fig = calculate_doc_average_word2vec(filter_model, article_titles)
                t = plot({'data': fig},
                         output_type='div')
                return JsonResponse({'data': t, 'dragmode': 'lasso'}, safe=True)
            except RuntimeError as e:
                print("Runtime error", e)
        else:
            fig = px.scatter()
            fig.update_layout(
                xaxis={"visible": False},
                yaxis={"visible": False},
                annotations=[
                    {
                        "text": "Sorry!! This view cannot be populated with just one result",
                        "xref": "paper",
                        "yref": "paper",
                        "showarrow": False,
                        "font": {
                            "size": 28
                        }
                    }
                ]
            )
            t = plot({'data': fig},
                     output_type='div')
            tt = {}
            return JsonResponse({'data': t}, safe=True)

    else:
        print("Error occured")


@csrf_exempt
def update_article_view(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        selected_article_points = json.loads(request.body)
        main_articles = Article.objects.none()
        for article_point in selected_article_points:
            main_articles |= Article.objects.filter(article_title__exact=article_point)

        article_title, published_date, article_count, total_count = get_article_published_year_and_count(main_articles)
        t = render_to_string('article_page_view.html', {'data': main_articles, 'article_title': article_title,
                                                        'total_count': total_count})
        tt = {'published_data': published_date, 'article_count': article_count, 'total_count': total_count,
              'article_title': article_title}
        return JsonResponse({'data': t, 'data2': tt}, safe=False)


@csrf_exempt
def update_article_view_from_time_chart(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        article_years = json.loads(request.body)

        main_articles = Article.objects.filter(published_date__gte=article_years[0], published_date__lte=article_years[1])
    # main_articles = json.loads(request.body)

        article_titles, published_date, article_count, total_count = get_article_published_year_and_count(main_articles)

        fig = calculate_doc_average_word2vec(filter_model, article_titles)
        tt = plot({'data': fig}, output_type='div')

        t = render_to_string('article_page_view.html', {'data': main_articles, 'total_count':total_count})
        return JsonResponse({'data': t, 'data2': tt}, safe=False)


@csrf_exempt
def populate_on_search(request):
    # This is for search
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        url_parameter = request.GET.get("q")
        print("search_item", url_parameter)
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

        article_title, published_date, article_count, total_count = get_article_published_year_and_count(articles)

        html = render_to_string(
            template_name="component_view.html",
            context={'data': articles, 'article_title': article_title, 'published_date': published_date,
                     'article_count': article_count}
        )
        embedding_view_data = {'article_titles': article_title, 'total_count': total_count}
        return JsonResponse({'data': html, 'embedding_view_data': embedding_view_data}, safe=False)


def get_article_published_year_and_count(main_articles):
    article_title = [article.article_title for article in main_articles]
    published_date_data = list(main_articles
                               .values('published_date')
                               .annotate(dcount=Count('published_date'))
                               .order_by()
                               )

    published_date = list(d['published_date'] for d in published_date_data)
    article_count = list(d['dcount'] for d in published_date_data)
    total_count = main_articles.count()
    return article_title, published_date, article_count, total_count
