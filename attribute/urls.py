from django.urls import path
from .view.color import color
from .view.size import size
from .view.planter import planter
from .view.planterSize import planter_size
from .view.plantersByPlanterSize import get_planters_by_planter_size
from .view.weight import weight

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

    path('weight/', weight, name='weight'),
    path('weight/<int:pk>/', weight, name='weight'),

    # Get all planters by planter size
    path('plantersByPlanterSize/<int:pk>/', get_planters_by_planter_size, name='get_planters_by_planter_size'),
]