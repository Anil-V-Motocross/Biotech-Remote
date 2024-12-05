from django.urls import path
from .views.register import register
from .views.login import login
from .views.role import create_group_and_assign_permissions

urlpatterns = [
    path('register/', register , name='register'),
    path('login/', login, name='login'),
    # path('logout/', views.logout, name='logout'),

    path('create-group/', create_group_and_assign_permissions, name='create_group_and_assign_permissions'),
]