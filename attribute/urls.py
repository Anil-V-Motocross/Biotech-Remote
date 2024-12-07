from django.urls import path
from .view.color import color

app_name = 'attribute'

urlpatterns = [
    path('color/', color, name='color'),
]