from django.urls import path
from .view.order import order

app_name = 'order'

urlpatterns = [
    path('', order, name='order'),
    path('<int:pk>/', order, name='order'),
]