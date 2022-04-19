import json
import os

import django

CUR_DIR = os.path.basename(os.getcwd())

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'visBioMed.settings')
django.setup()

from filter import Article


# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
# django.setup()


# use it when necessary
def reset_db():
    try:
        os.remove('db.sqlite3')
    except:
        pass
    os.system('python manage.py migrate')
    print("Database reseted.")


def add_articles():
    with open('articles_data/all_articles_with_thumbnail.json') as f:
        articles = json.load(f)
        table_contet_exist = False
    for article in articles:
        article_title = article["article_title"]
        article_authors = article["article_authors"]
        publisher = article["publisher"]
        published_date = article["published_date"]
        ISSN = article["ISSN"]
        ISBN = article["ISBN"]
        DOI = article["DOI"]
        thumbnail = article["thumbnail"]

        try:
            table_contet_exist = False
            article = Article.objects.create(
                article_title=article_title, article_authors=article_authors, publisher=publisher,
                published_date=published_date, ISSN=ISSN, ISBN=ISBN, DOI=DOI, thumbnail_path=thumbnail
            )
        except:
            table_contet_exist = True

    if table_contet_exist:
        print("Values cannot be duplicated")


if __name__ == '__main__':
    add_articles()
    print("Done")
