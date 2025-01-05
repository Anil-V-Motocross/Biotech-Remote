from django.urls import path
from .view.carrier import carrier, public_carrier

app_name = 'carrier'

urlpatterns = [
    path('', carrier, name='carrier'),
    path('<int:pk>/', carrier, name='carrier'),

    # Public APIs
    path('publicCarrier/', public_carrier, name='public_carrier'),
]