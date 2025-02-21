from django.urls import path
from .views.register import register_staff
from .views.login import login_staff
from .views.role import create_group_and_assign_permissions, get_permissions
from .views.register_mobile import register_mobile, validate_otp, register
from .views.all_users import all_users
from .views.profile import profile, address

name = 'account'

urlpatterns = [
    path('registerWithMobile/', register_mobile, name='register_mobile'),
    path('validateOtp/', validate_otp, name='validate_otp'),
    path('register/', register , name='register'),
    path('register-staff/', register_staff, name='register_staff'),
    path('login-staff/', login_staff, name='login_staff'),
    path('all_users/', all_users, name='all_users'),
    path('all_users/<int:pk>/', all_users, name='all_users'),

    path('create-group/', create_group_and_assign_permissions, name='create_group_and_assign_permissions'),
    path('get-permissions/', get_permissions, name='get_permissions'),
    
    path('profile/', profile,name='profile'),
    
    path('address/',address,name='address'),
    path('address/<int:pk>/',address,name='address'),
    # path('editprofile/<int:pk>/',edituser_profile,name='editprofile'),
]
