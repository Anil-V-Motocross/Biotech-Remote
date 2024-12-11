from django.urls import path
from .view.store import store

app_name = 'store'

urlpatterns = [
    path('', store, name='store'),
    path('<int:pk>/', store, name='store'),
]