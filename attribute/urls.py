from django.urls import path
from .view.color import color
from .view.size import size
from .view.planter import planter
from .view.planterSize import planter_size

app_name = 'attribute'

urlpatterns = [
    path('color/', color, name='color'),
    path('color/<int:pk>/', color, name='color'),

    path('size/', size, name='size'),
    path('size/<int:pk>/', size, name='size'),

    path('planter/', planter, name='planter'),
    path('planter/<int:pk>/', planter, name='planter'),

    path('planterSize/', planter_size, name='planterSize'),
    path('planterSize/<int:pk>/', planter_size, name='planterSize'),
]