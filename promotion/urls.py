from django.urls import path
from .view.banner import banner
from .view.contact_us import contact_us

app_name = 'promotion'

urlpatterns = [
    path('banner/', banner, name='banner'),
    path('banner/<int:pk>/', banner, name='banner'),

    path('contactUs/', contact_us, name='contact_us'),
]