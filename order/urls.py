from django.urls import path
from .view.order import order
from .view.cart import cart
from .view.wishlist import wishlist
from .view.order_item import order_item

app_name = 'order'

urlpatterns = [
    path('', order, name='order'),
    path('<int:pk>/', order, name='order'),
    
    path('orderItem/', order_item, name='order_item'),
    
    path('cart/', cart, name='cart'),
    path('cart/<int:pk>/', cart, name='cart'),
    
    path('wishlist/', wishlist, name='wishlist'),
    path('wishlist/<int:pk>/', wishlist, name='wishlist'),
]