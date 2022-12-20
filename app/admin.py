from django.contrib import admin

# Register your models here.
from app.models.category import Category, Subcategory
from app.models.article import Article

admin.site.register(Category)
admin.site.register(Subcategory)
admin.site.register(Article)
