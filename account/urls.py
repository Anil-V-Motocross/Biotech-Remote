from django.urls import path
from .views.register import register_staff
from .views.login import login_staff
from .views.role import create_group_and_assign_permissions, get_permissions
from .views.register_mobile import register_mobile, validate_otp, register

name = 'account'

urlpatterns = [
    path('registerWithMobile/', register_mobile, name='register_mobile'),
    path('validateOtp/', validate_otp, name='validate_otp'),
    path('register/', register , name='register'),
    path('register-staff/', register_staff, name='register_staff'),
    path('login-staff/', login_staff, name='login_staff'),
    # path('logout/', views.logout, name='logout'),

    path('create-group/', create_group_and_assign_permissions, name='create_group_and_assign_permissions'),
    path('get-permissions/', get_permissions, name='get_permissions')
]