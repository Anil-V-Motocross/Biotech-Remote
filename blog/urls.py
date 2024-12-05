from django.urls import path
from .view.test import test

app_name = 'blog'

urlpatterns = [
    path('test/', test, name='test'),
]