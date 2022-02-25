from django.db import models


class Category(models.Model):
    category_name = models.CharField(max_length=50)

    class Meta:
        ordering = ['-category_name']

    # to save the data
    def register(self):
        self.save()

    @staticmethod
    def get_all_categories():
        return Category.objects.all()

    def __str__(self):
        return self.category_name


class Subcategory(models.Model):

    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    label = models.CharField(max_length=50)

    # to save the data
    def register(self):
        self.save()

    @staticmethod
    def get_all_labels():
        return Subcategory.objects.all()

    class Meta:
        ordering = ['-label']

    def __str__(self):
        return self.label
