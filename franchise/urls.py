from django.urls import path
from .view.franchise import franchise

app_name = 'franchise'

urlpatterns = [
    path('', franchise, name='franchise'),
]