import json

# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
# django.setup()
"""
If you want to update data file i.e all_articles_with_metadata.json, then use this particular script.
"""


def add_thumbnail_to_article():
    path = '../static/thumbnails/'
    with open('../articles_data/all_articles_metadata.json') as f:
        articles = json.load(f)
    for article in articles:
        thumbnail = article["article_title"].replace(" ", "_").replace('/', '-') + ".jpg"
        # {**article, **{"thumbnail": path + thumbnail}}
        article.update({"thumbnail": path + thumbnail})

    json_string = json.dumps(articles)
    with open('../articles_data/all_articles_with_thumbnail_metadata.json', 'x') as f:
        f.write(json_string)


if __name__ == '__main__':
    add_thumbnail_to_article()
