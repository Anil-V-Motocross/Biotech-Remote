from django.urls import path
# from .views.register import register
from .views.login import login
from .views.role import create_group_and_assign_permissions
from .views.register_mobile import register_mobile, validate_otp, register

urlpatterns = [
    path('registerWithMobile/', register_mobile, name='register_mobile'),
    path('validateOtp/', validate_otp, name='validate_otp'),
    path('register/', register , name='register'),
    path('login/', login, name='login'),
    # path('logout/', views.logout, name='logout'),

    path('create-group/', create_group_and_assign_permissions, name='create_group_and_assign_permissions'),
]