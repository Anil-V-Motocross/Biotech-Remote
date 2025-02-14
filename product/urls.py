from django.urls import path
from .view.main_product import main_product
from .view.add_category_subcategory_tags import add_category_subcategory_tags
from .view.product import product
from .view.home_products import home_products
from .view.default_product import default_product
from .view.filter_product import filter_product
from .view.products_of_main_product import products_of_main_product
from .view.subcategory_products import subcategory_products
from .view.sort_by import sort_by

app_name = 'product'

urlpatterns = [
    path('', main_product, name='main_product'),
    path('addCategorySubcategoryTags/', add_category_subcategory_tags, name='add_category_subcategory_tags'),

    path('productsOfMainProduct/<int:pk>/', products_of_main_product, name='products_of_main_product'),

    # manage products
    path('product/', product, name='product'),


    # customer urls
    path('homeProducts/', home_products, name='home_products'),
    path('defaultProduct/<int:product_id>/', default_product, name='default_product'),
    path('filterProduct/<int:pk>/', filter_product, name='filter_product'),
    
    path('subcategoryProducts/<int:subcategory_id>/', subcategory_products, name='subcategory_products'),
    path('sortBy/', sort_by, name='sort_by'),
]