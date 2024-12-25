from django.urls import path
from .view.main_product import main_product
from .view.add_category_subcategory_tags import add_category_subcategory_tags
from .view.product import product
from .view.home_products import home_products
from .view.default_product import default_product

app_name = 'product'

urlpatterns = [
    path('', main_product, name='main_product'),
    path('addCategorySubcategoryTags/', add_category_subcategory_tags, name='add_category_subcategory_tags'),

    # manage products
    path('product/', product, name='product'),

    path('homeProducts/', home_products, name='home_products'),
    path('defaultProduct/<int:product_id>/', default_product, name='default_product'),
]