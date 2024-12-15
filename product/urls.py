from django.urls import path
from .view.product import product
from .view.add_category_subcategory_tags import add_category_subcategory_tags

app_name = 'product'

urlpatterns = [
    path('', product, name='product'),
    path('addCategorySubcategoryTags/', add_category_subcategory_tags, name='add_category_subcategory_tags'),
]