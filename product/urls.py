from django.urls import path
from .view.product import product

app_name = 'product'

urlpatterns = [
    path('', product, name='product'),
]