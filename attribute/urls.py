from django.urls import path
from .view.color import color
from .view.size import size

app_name = 'attribute'

urlpatterns = [
    path('color/', color, name='color'),
    path('size/', size, name='size'),
]