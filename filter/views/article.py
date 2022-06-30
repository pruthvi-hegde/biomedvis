import json
import re

from django.db.models import Count
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from plotly.offline import plot

from ..doc_to_vec import Doc2Vec
from ..models.article import Article
from ..models.category import Category, Subcategory

# filter_model = FiltersConfig.model
main_articles = Article.objects.none()
filtered_articles = Article.objects.none()
selected_model = "all_minilm_l6_v2"
article_title = ""
articles = ""


# Article List
def article_list(request):
    global main_articles
    global filtered_articles
    global article_title
    global articles
    articles = Article.objects.all().order_by('-id')

    # This part is to fetch all categories and subcategories from categories model.
    categories = Category.get_all_categories()

    categories_data = {}
    for cat in categories:
        categories_name = cat.category_name
        categories_data[categories_name] = Subcategory.objects.filter(category__exact=cat)

    article_title, published_date, article_count, total_count = get_article_published_year_and_count(articles)
    articles = articles
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
    global article_title
    global selected_model
    articles_filtered = Article.objects.none()
    if len(filter_values) != 0:
        for categories in filter_values.values():
            for cat in categories:
                articles_filtered |= filtered_articles.filter(Q(abstract__icontains=cat) |
                                                              Q(article_title__icontains=cat))
    else:
        articles_filtered = Article.objects.all().order_by('-id')

    article_title, published_date, article_count, total_count = get_article_published_year_and_count(articles_filtered)

    plot_object = get_embedding_view_data(article_title)

    article_view_data = render_to_string('component_view.html', {'data': articles, 'article_title': article_title,
                                                                 'published_date': published_date,
                                                                 'article_count': article_count,
                                                                 'total_count': total_count,
                                                                 })
    time_view_data = {'published_data': published_date, 'article_count': article_count, 'total_count': total_count,
                      'article_title': article_title}
    main_articles = articles
    return JsonResponse({'article_view_data': article_view_data, 'time_view_data': time_view_data,
                         'embedding_view_data': plot_object, 'selected_model': selected_model}, safe=False)


@csrf_exempt
def update_article_view(request):
    if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        selected_article_points = json.loads(request.body)
        global filtered_articles
        global main_articles
        global article_title
        articles = Article.objects.none()
        for article_point in selected_article_points:
            articles |= filtered_articles.filter(article_title__exact=article_point)

        article_title, published_date, article_count, total_count = get_article_published_year_and_count(articles)
        article_view_data = render_to_string('article_page_view.html',
                                             {'data': articles, 'article_title': article_title,
                                              'total_count': total_count})
        time_view_data = {'published_data': published_date, 'article_count': article_count, 'total_count': total_count,
                          'article_title': article_title}
        main_articles = articles
        return JsonResponse({'article_view_data': article_view_data, 'time_view_data': time_view_data}, safe=False)


@csrf_exempt
def update_article_view_from_time_chart(request):
    global filtered_articles
    global main_articles
    global article_title
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
        article_title, published_date, article_count, total_count = get_article_published_year_and_count(articles)
        plot_object = get_embedding_view_data(article_title)

        html = render_to_string('article_page_view.html', {'data': articles, 'total_count': total_count})
        filtered_articles = articles
        return JsonResponse({'article_view_data': html, 'embedding_view_data': plot_object}, safe=False)


@csrf_exempt
def populate_on_search(request):
    # This is for search
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        global filtered_articles
        global main_articles
        global article_title
        global selected_model
        query_parameter = request.GET.get("q")
        query_parameter = re.sub(' +', ' ', query_parameter)
        if query_parameter:
            articles = Article.objects.none()
            if re.match('^\d{4}$', query_parameter):
                searched_articles = filtered_articles.filter(Q(published_date__exact=query_parameter))
            else:
                searched_articles = filtered_articles.filter(
                    Q(abstract__icontains=query_parameter) | Q(article_title__icontains=query_parameter) | Q(
                        article_authors__icontains=query_parameter))
            if list(searched_articles) == list(articles):
                searched_articles = articles
                # url_parameter = url_parameter.split(" ")
                # for query_word in url_parameter:
                #     main_articles |= Article.objects.filter(abstract__icontains=query_word)

        elif not query_parameter:
            searched_articles = filtered_articles
        else:
            searched_articles = filtered_articles

        article_title, published_date, article_count, total_count = get_article_published_year_and_count(
            searched_articles)
        plot_object = get_embedding_view_data(article_title)

        html = render_to_string(
            template_name="component_view.html",
            context={'data': searched_articles, 'article_title': article_title, 'published_date': published_date,
                     'article_count': article_count, 'total_count': total_count}
        )
        time_view_data = {'article_titles': article_title,
                          'published_date': published_date,
                          'article_count': article_count}

        main_articles = searched_articles
        return JsonResponse({'article_view_data': html, 'time_view_data': time_view_data,
                             'embedding_view_data': plot_object, 'selected_model': selected_model}, safe=False)


def get_article_published_year_and_count(articles_data):
    global articles
    articles = articles_data
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
                "article_title": f"{article.article_title} ({article.published_date})",
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
        }
    }
    if len(article_titles) > 0:
        fig = Doc2Vec(selected_model).calculate_doc_average(article_titles)
        plot_object = plot({'data': fig}, output_type='div', config=config)
    else:
        plot_object = "<div class='text-center' style='padding-top: 12rem'>" \
                      "This plot will be loaded if the filtered articles are atleast 1</div>"

    return plot_object
