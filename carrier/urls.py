from django.urls import path
from .view.carrier import carrier

app_name = 'carrier'

urlpatterns = [
    path('', carrier, name='carrier'),
    path('<int:pk>/', carrier, name='carrier'),
]