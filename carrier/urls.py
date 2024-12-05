from django.urls import path
from .view.test import test

app_name = 'carrier'

urlpatterns = [
    path('test/', test, name='test'),
]