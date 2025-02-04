from django.urls import path
from .view.order import order
from .view.cart import cart
from .view.wishlist import wishlist
from .view.user_orders import user_orders
from .view.place_order import place_order

app_name = 'order'

urlpatterns = [
    path('', order, name='order'),
    path('<int:pk>/', order, name='order'),
    
    path('cart/', cart, name='cart'),
    path('cart/<int:pk>/', cart, name='cart'),
    
    path('wishlist/', wishlist, name='wishlist'),
    path('wishlist/<int:pk>/', wishlist, name='wishlist'),
    
    # Following URLs is checkout
    # path('checkout/', ch, name='checkout'),
    
    # Following URLs are for user orders
    path('placeOrder/', place_order, name='place_order'),
    path('userOrders/<int:customer_id>/', user_orders, name='user_orders'),
    
]