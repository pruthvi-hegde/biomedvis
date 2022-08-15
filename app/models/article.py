from django.db import models


class Article(models.Model):
    article_title = models.CharField(max_length=200, unique=True)
    thumbnail_path = models.CharField(max_length=300)
    article_authors = models.CharField(max_length=200)
    publisher = models.CharField(max_length=200)
    published_year = models.IntegerField()
    ISSN = models.CharField(max_length=100)
    ISBN = models.CharField(max_length=100)
    DOI = models.CharField(max_length=150, unique=True)
    keywords = models.CharField(max_length=2000, default='')
    abstract = models.CharField(max_length=5000)

    def register(self):
        self.save()

    @staticmethod
    def get_all_articles():
        return Article.objects.all()

    class Meta:
        app_label = 'app'

    def __str__(self):
        return self.article_title
