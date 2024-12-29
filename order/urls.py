from django.urls import path
from .view.order import order
from .view.cart import cart
from .view.wishlist import wishlist

app_name = 'order'

urlpatterns = [
    path('', order, name='order'),
    path('<int:pk>/', order, name='order'),
    
    path('cart/', cart, name='cart'),
    path('cart/<int:pk>/', cart, name='cart'),
    
    path('wishlist/', wishlist, name='wishlist'),
    path('wishlist/<int:pk>/', wishlist, name='wishlist'),
]