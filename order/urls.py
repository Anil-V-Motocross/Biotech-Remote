from django.urls import path
from .view.order import order
from .view.cart import cart

app_name = 'order'

urlpatterns = [
    path('', order, name='order'),
    path('<int:pk>/', order, name='order'),
    
    path('cart/', cart, name='cart'),
    path('cart/<int:pk>/', cart, name='cart'),
]