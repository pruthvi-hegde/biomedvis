import ast
import json
import re

from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from plotly.offline import plot
from django.db.models import Q

from ..apps import FiltersConfig
from ..content_processor import ContentUtil
from ..doc_to_vec import Doc2Vec
from ..models.article import Article
from ..models.category import Category, Subcategory

# filter_model = FiltersConfig.model
main_articles = Article.objects.none()
filtered_articles = Article.objects.none()
selected_model = None


# Article List
def article_list(request):
    global main_articles
    global filtered_articles
    articles = Article.objects.all().order_by('-id')

    # This part is to fetch all categories and subcategories from categories model.
    categories = Category.get_all_categories()

    categories_data = {}
    for cat in categories:
        categories_name = cat.category_name
        categories_data[categories_name] = Subcategory.objects.filter(category__exact=cat)

    article_title, published_date, article_count, total_count = get_article_published_year_and_count(articles)
    filtered_articles = articles
    main_articles = articles

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
    global filtered_articles
    global main_articles
    global selected_model
    articles = Article.objects.none()
    if len(filter_values) != 0:
        for categories in filter_values.values():
            for cat in categories:
                articles |= filtered_articles.filter(abstract__icontains=cat)
    else:
        articles = Article.objects.all().order_by('-id')

    article_title, published_date, article_count, total_count = get_article_published_year_and_count(articles)

    if len(articles) > 3:
        fig = Doc2Vec(selected_model).calculate_doc_average(article_title)
        plot_object = plot({'data': fig}, output_type='div')
    else:
        plot_object = "<div class='text-center' style='padding-top: 12rem'>" \
                      "This plot will be loaded if the filtered articles are atleast 3</div>"

    t = render_to_string('component_view.html', {'data': articles, 'article_title': article_title,
                                                 'published_date': published_date,
                                                 'article_count': article_count,
                                                 'total_count': total_count,
                                                 })
    tt = {'published_data': published_date, 'article_count': article_count, 'total_count': total_count,
          'article_title': article_title}
    main_articles = articles
    return JsonResponse({'data': t, 'data2': tt, 'data3': plot_object}, safe=False)


@csrf_exempt
def create_embedding_view(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        global selected_model
        response = json.loads(request.body)
        article_titles = ast.literal_eval(response['articleData'])
        selected_model = response['selectedModel']
        if len(article_titles) > 3:
            try:
                fig = Doc2Vec(response['selectedModel']).calculate_doc_average(article_titles)
                t = plot({'data': fig},
                         output_type='div')
                return JsonResponse({'data': t}, safe=True)
            except RuntimeError as e:
                print("Runtime error", e)
        else:
            html = "<div class='text-center' style='padding-top: 12rem'>" \
                   "This plot will be loaded if the filtered articles are at least 4</div>"
            return JsonResponse({'data': html}, safe=True)

    else:
        print("Error occured")


@csrf_exempt
def update_article_view(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        selected_article_points = json.loads(request.body)
        global filtered_articles
        global main_articles
        articles = Article.objects.none()
        for article_point in selected_article_points:
            articles |= filtered_articles.filter(article_title__exact=article_point)

        article_title, published_date, article_count, total_count = get_article_published_year_and_count(articles)
        t = render_to_string('article_page_view.html', {'data': articles, 'article_title': article_title,
                                                        'total_count': total_count})
        tt = {'published_data': published_date, 'article_count': article_count, 'total_count': total_count,
              'article_title': article_title}
        main_articles = articles
        return JsonResponse({'data': t, 'data2': tt}, safe=False)



@csrf_exempt
def update_article_view_from_time_chart(request):
    global filtered_articles
    global main_articles
    global selected_model
    print(selected_model)
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        article_data = json.loads(request.body)

        if article_data['loadFirstTime']:
            articles = Article.objects.filter(published_date__gte=article_data['minYear'],
                                              published_date__lte=article_data['maxYear'])
        else:
            if article_data['minYear'] == article_data['maxYear']:
                articles = main_articles.filter(published_date=article_data['minYear'])
            else:
                articles = main_articles.filter(published_date__gte=article_data['minYear'],
                                                published_date__lte=article_data['maxYear'])
        # main_articles = json.loads(request.body)
        article_titles, published_date, article_count, total_count = get_article_published_year_and_count(articles)

        if len(articles) > 3:
            fig = Doc2Vec(selected_model).calculate_doc_average(article_titles)
            plot_object = plot({'data': fig}, output_type='div')
        else:
            plot_object = "<div class='text-center' style='padding-top: 12rem'>" \
                          "This plot will be loaded if the filtered articles are atleast 3</div>"

        html = render_to_string('article_page_view.html', {'data': articles, 'total_count': total_count})
        filtered_articles = articles
        return JsonResponse({'data': html, 'data2': plot_object}, safe=False)


@csrf_exempt
def populate_on_search(request):
    # This is for search
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        global filtered_articles
        global main_articles
        query_parameter = request.GET.get("q")
        if query_parameter:
            articles = Article.objects.none()
            searched_articles = filtered_articles.filter(Q(abstract__icontains=query_parameter) |
                                                         Q(article_title__icontains=query_parameter))
            if list(searched_articles) == list(articles):
                # url_parameter = url_parameter.split(" ")
                # for query_word in url_parameter:
                #     main_articles |= Article.objects.filter(abstract__icontains=query_word)

                searched_articles = articles
        elif not query_parameter:
            searched_articles = filtered_articles
        else:
            searched_articles = filtered_articles

        article_title, published_date, article_count, total_count = get_article_published_year_and_count(
            searched_articles)

        html = render_to_string(
            template_name="component_view.html",
            context={'data': searched_articles, 'article_title': article_title, 'published_date': published_date,
                     'article_count': article_count, 'total_count': total_count}
        )
        article_view_data = {'article_titles': article_title,
                             'published_date': published_date,
                             'article_count': article_count}
        main_articles = searched_articles
        return JsonResponse({'data': html, 'data2': article_view_data}, safe=False)


def get_article_published_year_and_count(articles):
    article_title = [article.article_title for article in articles]
    published_date_data = list(articles
                               .values('published_date')
                               .annotate(dcount=Count('published_date'))
                               .order_by()
                               )

    published_date = list(d['published_date'] for d in published_date_data)
    article_count = list(d['dcount'] for d in published_date_data)
    total_count = articles.count()
    return article_title, published_date, article_count, total_count


@csrf_exempt
def populate_details_view(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        article_title = json.loads(request.body)
        article_details = Article.objects.filter(article_title__exact=article_title)
        article_info = {}
        for article in article_details:
            article_info = {
                "article_title": f"{article.article_title}( {article.published_date})",
                "abstract": article.abstract,
                "articleDOI": article.DOI,
                "articleThumbnail": article.thumbnail_path

            }
        return JsonResponse({'data': article_info}, safe=False)


