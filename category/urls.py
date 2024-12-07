from django.urls import path
from .view.test import test

app_name = 'category'

urlpatterns = [
    path('test/', test, name='test'),
]