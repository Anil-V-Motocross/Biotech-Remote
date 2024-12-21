from django.urls import path
from .view.main_product import main_product
from .view.add_category_subcategory_tags import add_category_subcategory_tags
from .view.product import product

app_name = 'product'

urlpatterns = [
    path('', main_product, name='main_product'),
    path('addCategorySubcategoryTags/', add_category_subcategory_tags, name='add_category_subcategory_tags'),

    # manage products
    path('product/', product, name='product'),
]