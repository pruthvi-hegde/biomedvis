from django.contrib import admin

# Register your models here.
from .models.category import Category, Subcategory
from .models.article import Article

admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Article)
