from django.urls import path
from .view.product import product
from .view.main_product import main_product
from .view.add_category_subcategory_tags import add_category_subcategory_tags
from .view.product import product
from .view.home_products import home_products
from .view.default_product import default_product
from .view.filter_product import filter_product
from .view.products_of_main_product import products_of_main_product
from .view.subcategory_products import subcategory_products
from .view.sort_by import sort_by
from .view.update_default_product import update_default_product
from .view.stock_check import check_product_quantity
from .view.search_product import search_products
from .view.category_product import category_products, subcategory_products
from .view.ratings_and_reviews import rating_review_create
from .view.search_main_product_in_admin  import admin_search_products
from .view.recently_viewed import RecentlyViewedProductsView
from .view.inventory_products import list_products
from .view.offers import list_discounted_products

app_name = 'product'

urlpatterns = [
    path('', main_product, name='main_product'),
    path('<int:pk>/', main_product, name='main_product_update_delete'),
    path('addCategorySubcategoryTags/', add_category_subcategory_tags, name='add_category_subcategory_tags'),

    path('productsOfMainProduct/<int:pk>/', products_of_main_product, name='products_of_main_product'),

    # manage products
    path('product/', product, name='product'),
    path('updateDefaultProduct/<int:product_id>/', update_default_product, name='update_default_product'),

    # customer urls
    path('homeProducts/', home_products, name='home_products'),
    path('defaultProduct/<int:product_id>/', default_product, name='default_product'),
    path('filterProduct/<int:pk>/', filter_product, name='filter_product'),
    path('recentlyViewed/', RecentlyViewedProductsView.as_view(), name='recently_viewed_products'),
    
    path('subcategoryProducts/<int:subcategory_id>/', subcategory_products, name='subcategory_products'),
    path('sortBy/', sort_by, name='sort_by'),

    path('stockCheck/<int:product_id>/', check_product_quantity, name='stock_check'),

    path('searchProducts/', search_products, name='search_products'),
    path('category-products/<int:pk>/', category_products, name='category-products'),
    path('subcategory-products/<int:pk>/', subcategory_products, name='subcategory-products'),
    path('offerProducts/', list_discounted_products, name='offer_products'),

    path('ratingAndReviews/', rating_review_create, name='rating_and_review'),
    path('ratingAndReviews/<int:main_product_id>/', rating_review_create, name='rating_and_review'),
    
    # admin
    path('adminProductSearch/', admin_search_products, name='admin_product_search'),
    path('adminInventoryProducts/', list_products, name='inventory_products'),
]