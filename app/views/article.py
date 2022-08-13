import json
import re

from django.db.models import Count
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from plotly.offline import plot

from ..embeddings_loarder import Doc2Vec
from ..models.article import Article
from ..models.category import Category, Subcategory

# filter_model = FiltersConfig.model
all_articles = Article.objects.all().order_by('-id')
filtered_articles = Article.objects.all().order_by('-id')
selected_model = "allenai_specter"
article_title = ""

search_term_global = ""
filter_values_global = {}
year_global = {'min_year': 2008,
               'max_year': 2021}
selected_article_points_global = []


# Article List
def article_list(request):
    global all_articles
    global filtered_articles
    global article_title
    global search_term_global
    global filter_values_global
    global year_global
    global selected_article_points_global

    search_term_global = ""
    filter_values_global = {}
    year_global = {'min_year': 2008,
                   'max_year': 2021}
    selected_article_points_global = []

    # This part is to fetch all categories and subcategories from categories model.
    categories = Category.get_all_categories()

    categories_data = {}
    for cat in categories:
        categories_name = cat.category_name
        categories_data[categories_name] = Subcategory.objects.filter(category__exact=cat)

    article_title, published_year, article_count, total_count = get_article_published_year_and_count(all_articles)

    # This should execute for all
    return render(request, 'main.html',
                  {
                      'data': all_articles,
                      'article_title': article_title,
                      'total_count': total_count,
                      'view_item': categories_data,
                      'published_year': published_year,
                      'article_count': article_count

                  })


def filter_data(request):
    global filter_values_global
    global selected_model
    global article_title
    filter_values = dict(request.GET)
    filter_values_global = filter_values

    result_set = filter(True)
    result_set_v2 = filter(False)

    article_title, published_year, article_count, total_count = get_article_published_year_and_count(result_set_v2)
    embedding_view_data = get_embedding_view_data(article_title)
    article_view_data = render_to_string('components.html', {'data': result_set, 'article_title': article_title,
                                                             'published_year': published_year,
                                                             'article_count': article_count,
                                                             'total_count': total_count,
                                                             })
    time_view_data = {'published_data': published_year, 'article_count': article_count, 'total_count': total_count,
                      'article_title': article_title}
    return JsonResponse({'article_view_data': article_view_data, 'time_view_data': time_view_data,
                         'embedding_view_data': embedding_view_data, 'selected_model': selected_model}, safe=False)


@csrf_exempt
def update_article_view_from_lasso_box_select(request):
    global selected_article_points_global
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        selected_article_points_global = json.loads(request.body)

        result_set = filter(True)
        result_set_v2 = filter(False)

        article_title, published_year, article_count, total_count = get_article_published_year_and_count(result_set_v2)
        article_view_data = render_to_string('articles_page_view.html',
                                             {'data': result_set, 'article_title': article_title,
                                              'total_count': total_count})

        time_view_data = {'published_year': published_year, 'article_count': article_count, 'total_count': total_count,
                          'article_title': article_title}
        return JsonResponse({'article_view_data': article_view_data, 'time_view_data': time_view_data}, safe=False)


@csrf_exempt
def update_article_view_from_time_chart(request):
    global article_title
    global year_global
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        article_data = json.loads(request.body)

        if article_data['minYear'] != '':
            year_global['min_year'] = article_data['minYear']

        if article_data['maxYear'] != '':
            year_global['max_year'] = article_data['maxYear']

        result_set = filter(True)

        # main_articles = json.loads(request.body)
        article_title, published_year, article_count, total_count = get_article_published_year_and_count(result_set)
        plot_object = get_embedding_view_data(article_title)

        html = render_to_string('articles_page_view.html', {'data': result_set, 'total_count': total_count})
        return JsonResponse({'article_view_data': html, 'embedding_view_data': plot_object}, safe=False)


@csrf_exempt
def populate_on_search(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        global search_term_global
        global article_title
        global selected_model

        query_parameter = request.GET.get("q")
        query_parameter = re.sub(' +', ' ', query_parameter)
        search_term_global = query_parameter

        result_set = filter(True)

        article_title, published_year, article_count, total_count = get_article_published_year_and_count(
            result_set)
        plot_object = get_embedding_view_data(article_title)

        html = render_to_string(
            template_name="components.html",
            context={'data': result_set, 'article_title': article_title, 'published_year': published_year,
                     'article_count': article_count, 'total_count': total_count}
        )
        time_view_data = {'article_titles': article_title,
                          'published_year': published_year,
                          'article_count': article_count}

        return JsonResponse({'article_view_data': html, 'time_view_data': time_view_data,
                             'embedding_view_data': plot_object, 'selected_model': selected_model}, safe=False)


def get_article_published_year_and_count(articles_data):
    article_title = [article.article_title for article in articles_data]
    published_year_data = list(articles_data
                               .values('published_year')
                               .annotate(dcount=Count('published_year'))
                               .order_by()
                               )

    published_year = list(d['published_year'] for d in published_year_data)
    article_count = list(d['dcount'] for d in published_year_data)
    total_count = articles_data.count()
    return article_title, published_year, article_count, total_count


@csrf_exempt
def populate_details_view(request):
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        article_title = json.loads(request.body)
        article_details = Article.objects.filter(article_title__exact=article_title)
        article_info = {}
        for article in article_details:
            article_info = {
                "article_title": f"{article.article_title} ({article.published_year})",
                "abstract": article.abstract,
                "articleDOI": article.DOI,
                "articleThumbnail": article.thumbnail_path

            }
        return JsonResponse({'data': article_info}, safe=False)


@csrf_exempt
def create_embedding_view(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        global selected_model
        global article_title
        response = json.loads(request.body)
        # article_titles = ast.literal_eval(response['articleData'])
        selected_model = response['selectedModel']
        plot_object = get_embedding_view_data(article_title)
        return JsonResponse({'embedding_view_data': plot_object})

    else:
        print("Error occured")


def get_embedding_view_data(article_titles):
    global selected_model
    config = {
        'toImageButtonOptions': {
            'format': 'png',  # one of png, svg, jpeg, webp
            'filename': 'custom_image',
            'height': 500,
            'width': 700,
            'scale': 1  # Multiply title/legend/axis/canvas sizes by this factor
        },
        'displayModeBar': True
    }
    if len(article_titles) > 0:
        fig = Doc2Vec(selected_model).visualise_doc_embeddings(article_titles)
        plot_object = plot({'data': fig}, output_type='div', config=config)
    else:
        plot_object = "<div class='text-center' style='padding-top: 12rem'>" \
                      "This plot will be loaded if the filtered articles are at least one</div>"

    return plot_object


def filter(isWithTimeFilter):
    global all_articles
    global article_title
    global filter_values_global
    global search_term_global
    global year_global
    global filtered_articles
    global selected_article_points_global

    result_articles = {}
    result_set = Article.objects.all()

    if len(filter_values_global) != 0:
        i = 0
        for categories in filter_values_global.values():
            temp_articles = Article.objects.none()

            for subcategory in categories:
                temp_articles |= all_articles.filter(Q(abstract__icontains=subcategory) |
                                                     Q(article_title__icontains=subcategory) | Q(
                    keywords__icontains=subcategory))

            result_articles[i] = temp_articles
            i = i + 1

        for item in result_articles.values():
            result_set = result_set & item

    else:
        result_set = all_articles

    if search_term_global:
        if re.match('^\d{4}$', search_term_global):
            result_set = result_set.filter(Q(published_year__exact=search_term_global))
        else:
            result_set = result_set.filter(
                Q(abstract__icontains=search_term_global) | Q(article_title__icontains=search_term_global) | Q(
                    article_authors__icontains=search_term_global))

    if isWithTimeFilter:
        if year_global['min_year'] == year_global['max_year']:
            result_set = result_set.filter(published_year=year_global['min_year'])
        else:
            result_set = result_set.filter(published_year__gte=year_global['min_year'],
                                           published_year__lte=year_global['max_year'])

    if selected_article_points_global:
        temp_selected = Article.objects.none()
        for article_point in selected_article_points_global:
            temp_selected |= result_set.filter(article_title__exact=article_point)

        result_set = temp_selected

    filtered_articles = result_set.all()
    return result_set
