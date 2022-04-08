import json


# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
# django.setup()


def add_thumbnail_to_article():
    path = '../static/thumbnails/'
    with open('articles_data/all_articles.json') as f:
        articles = json.load(f)
    for article in articles:
        thumbnail = article["article_title"].replace(" ", "_") + ".jpg"
        # {**article, **{"thumbnail": path + thumbnail}}
        article.update({"thumbnail": path + thumbnail})

    json_string = json.dumps(articles)
    with open('articles_data/all_articles_with_thumbnail.json', 'w') as f:
        f.write(json_string)


add_thumbnail_to_article()
