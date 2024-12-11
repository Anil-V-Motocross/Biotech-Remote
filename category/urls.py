from django.urls import path
from .view.category import category

app_name = 'category'

urlpatterns = [
    path('category/', category, name='category'),
    path('category/<int:pk>/', category, name='category'),

    path('subCategory/', category, name='subCategory'),
    path('subCategory/<int:pk>/', category, name='subCategory'),

]