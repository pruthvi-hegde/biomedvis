import json
import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "biomedvis.settings")
django.setup()

from app.models.article import Article
from app.models.category import Category
from app.models.category import Subcategory

"""
If you would like to add to add your data to DB, then use this file. 
"""


# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "web.settings")
# django.setup()


# Below code erases all the tables in your tables. Use it with caution.
def reset_db():
    try:
        os.remove('db.sqlite3')
    except:
        pass
    os.system('python manage.py migrate')
    print("Database reseted.")


def add_articles_to_article_table():
    with open('articles_data/all_articles_with_thumbnail_metadata.json') as f:
        articles = json.load(f)
        table_content_exist = False
    for article in articles:
        article_title = article["article_title"]
        article_authors = article["article_authors"]
        publisher = article["publisher"]
        published_year = article["published_year"]
        ISSN = article["ISSN"]
        ISBN = article["ISBN"]
        DOI = article["DOI"]
        thumbnail = article["thumbnail"]
        abstract = article["abstract"]
        keywords = article["keywords"]

        try:
            table_content_exist = False
            article = Article.objects.create(
                article_title=article_title, article_authors=article_authors, publisher=publisher,
                published_year=published_year, ISSN=ISSN, ISBN=ISBN, DOI=DOI, thumbnail_path=thumbnail,
                keywords=keywords,
                abstract=abstract

            )
            article.save()
        except Exception as e:
            print(e)
            table_content_exist = True

    if table_content_exist:
        print("Values cannot be duplicated")

def update_field():
    with open('articles_data/all_articles_with_thumbnail_metadata.json') as f:
        articles = json.load(f)
        # table_content_exist = False
    for article in articles:
        article_title = article["article_title"]
        thumbnail = article["thumbnail"]
        article = Article.objects.get(article_title=article_title)
        article.thumbnail_path = thumbnail
        article.save()

def populate_categories_and_subcategories_table():
    table_content_exist = False
    # categories = [
    #     "Species", "Scale", "Organ", "Dimension", "Data Source", "Algorithm", "Visual Computing Subfield"
    # ]
    cat_and_sub = {
        "Species": ["Bird", "Fruit Fly", "Human", "Mice"],
        "Scale": ["Cell", "Molecule", "Organism", "Population"],
        "Organ": ["Brain", "Eye", "Heart", "Lung", "Liver"],
        "Dimension": ["2D", "3D", "4D"],
        "Data Source": ["Angiography", "CT Scan", "fMRI", "MRI", "Tractography", "Tomography", "Ultrasound", "X-ray"],
        "Algorithm": ["Image Segmentation"],
        "Domain": ["Computer Graphics", "Image processing and Computer Vision",
                   "Human Computer Interaction"]

    }
    for cat in cat_and_sub:
        try:
            table_content_exist = False

            categories = Category.objects.create(category_name=cat)
            categories.save()
            for subcategory in cat_and_sub[cat]:
                subcategories = Subcategory(category=categories, label=subcategory)
                subcategories.save()
        except Exception as e:
            print(e)
            table_content_exist = True

    if table_content_exist:
        print("Values cannot be duplicated")


if __name__ == '__main__':
    # reset_db()
    update_field()
    # populate_categories_and_subcategories_table()
    print("Done")
