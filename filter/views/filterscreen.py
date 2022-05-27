import django.views.generic
from django.views.generic.list import ListView
from django.views.generic import TemplateView
from ..models.category import Category
from ..models.category import Subcategory


class CategoryList(TemplateView):
    # specify the model for list view
    model = Category
    template_name = 'filter.html'


    #template_name = 'filter/category_list.html'
    context_object_name = 'category'
    # paginate_by = 10
    #queryset = Category.objects.filter(category_name__exact='Organ')

    def get_context_data(self, **kwargs):
        context = super(CategoryList, self).get_context_data(**kwargs)
        categories = Category.get_all_categories()

        holder = {}
        for cat in categories:
            holder[cat] = Subcategory.objects.filter(category__exact=cat)


        context['view_item'] = holder
        return context
