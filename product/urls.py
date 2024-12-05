from django.urls import path
from .view.test import test

app_name = 'product'

urlpatterns = [
    path('test/', test, name='test'),
]