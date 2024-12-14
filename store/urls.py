from django.urls import path
from .view.store import store, store_list

app_name = 'store'

urlpatterns = [
    path('', store, name='store'),
    path('<int:pk>/', store, name='store'),

    path('store_list/', store_list, name='store_list'),
]