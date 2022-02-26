from django.db.models import Model, CharField, ForeignKey, BooleanField
from django.db import models
from tree.fields import PathField
from tree.models import TreeModelMixin


class Category(Model, TreeModelMixin):
    category_name = CharField(max_length=50)
    parent = ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE)
    path = PathField()
    public = BooleanField(default=False)

    class Meta:
        ordering = ('path',)

    # to save the data
    def register(self):
        self.save()

    # @staticmethod
    # def get_all_categories():
    #     return Category.objects.all()

    def __str__(self):
        return self.category_name


class Subcategory(Model, TreeModelMixin):

    category = ForeignKey(Category, on_delete=models.CASCADE, default=1)
    label = CharField(max_length=50)

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
