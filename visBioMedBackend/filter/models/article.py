from django.db import models


class Article(models.Model):
    article_title = models.CharField(max_length=200, unique=True)
    article_authors = models.CharField(max_length=50)
    publisher = models.CharField(max_length=50)
    published_date = models.CharField(max_length=50)
    ISSN = models.CharField(max_length=20)
    ISBN = models.CharField(max_length=20)
    DOI = models.CharField(max_length=50, unique=True)

    def register(self):
        self.save()

    @staticmethod
    def get_all_articles():
        return Article.objects.all()

    def __str__(self):
        return self.DOI

