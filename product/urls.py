from django.urls import path
from .view.main_product import main_product
from .view.add_category_subcategory_tags import add_category_subcategory_tags
from .view.product import product
from .view.home_products import home_products
from .view.default_product import default_product
from .view.filter_product import filter_product
from .view.products_of_main_product import products_of_main_product
app_name = 'product'

urlpatterns = [
    path('', main_product, name='main_product'),
    path('addCategorySubcategoryTags/', add_category_subcategory_tags, name='add_category_subcategory_tags'),

    path('productsOfMainProduct/<int:pk>/', products_of_main_product, name='products_of_main_product'),

    # manage products
    path('product/', product, name='product'),

    path('homeProducts/', home_products, name='home_products'),
    path('defaultProduct/<int:product_id>/', default_product, name='default_product'),
    path('filterProduct/<int:pk>/', filter_product, name='filter_product'),
]