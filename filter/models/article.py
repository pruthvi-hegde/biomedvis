from django.db import models


class Article(models.Model):
    article_title = models.CharField(max_length=200, unique=True)
    thumbnail_path = models.CharField(max_length=300)
    article_authors = models.CharField(max_length=50)
    publisher = models.CharField(max_length=50)
    published_date = models.IntegerField()
    ISSN = models.CharField(max_length=20)
    ISBN = models.CharField(max_length=20)
    DOI = models.CharField(max_length=50, unique=True)

    def register(self):
        self.save()

    @staticmethod
    def get_all_articles():
        return Article.objects.all()

    class Meta:
        app_label = 'filter'

    def __str__(self):
        return self.article_title
