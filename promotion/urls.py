from django.urls import path
from .view.banner import banner

app_name = 'promotion'

urlpatterns = [
    path('banner/', banner, name='banner'),
]