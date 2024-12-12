from django.urls import path
from .view.category import category, open_category
from .view.subCategory import subCategory, category_wise_subCategory

app_name = 'category'

urlpatterns = [
    path('', open_category, name='open_category'),
    path('', category, name='category'),
    path('category/', category, name='category'),
    path('category/<int:pk>/', category, name='category'),

    path('subCategory/', subCategory, name='subCategory'),
    path('subCategory/<int:pk>/', subCategory, name='subCategory'),
    path('categoryWiseSubCategory/<int:pk>/', category_wise_subCategory, name='category_wise_subCategory'),
]