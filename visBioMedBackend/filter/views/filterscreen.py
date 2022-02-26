from django.views.generic.list import ListView
from ..models.category import Category
from ..models.category import Subcategory


class CategoryList(ListView):
    # specify the model for list view
    model = Category


    #template_name = 'filter/category_list.html'
    context_object_name = 'category'
    # paginate_by = 10
    #queryset = Category.objects.filter(category_name__exact='Organ')

    def get_context_data(self, **kwargs):
        context = super(CategoryList, self).get_context_data(**kwargs)
        context['labels'] = Subcategory.get
        return context
