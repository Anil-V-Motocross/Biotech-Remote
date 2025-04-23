from django.urls import path
from .view.order import order
from .view.cart import cart
from .view.wishlist import wishlist
from .view.user_orders import user_orders
# from .view.place_order import place_order
# from .view.order_summary import order_summary
from .view.order_summary2 import order_summary
from .view.proceed_to_payment import proceed_to_payment
from .view.verify_payment import verify_payment
from .view.order_history import order_history
from .view.order_history_items import order_history_items
from .view.order_items import order_items
from .view.place_order2 import place_order
from .view.validate_coupon import validate_coupon
from .view.invoice import OrderInvoicePDFView
from .view.notifications import ProcessingOrdersCountView
from .view.return_order import request_return

app_name = 'order'

urlpatterns = [
    path('', order, name='order'),
    path('<int:pk>/', order, name='order'),
    path('notifications/', ProcessingOrdersCountView.as_view(), name='processing-orders-count'),
    
    path('orderItem/', order_items, name='order_items'),
    
    path('cart/', cart, name='cart'),
    path('cart/<int:pk>/', cart, name='cart'),
    
    path('wishlist/', wishlist, name='wishlist'),
    path('wishlist/<int:pk>/', wishlist, name='wishlist'),
    
    # Following URLs are for user orders
    path('placeOrder/', place_order, name='place_order'),
    path('orderSummary/', order_summary, name='order_summary'),
    path('proceedToPayment/', proceed_to_payment, name='proceed_to_payment'),
    path("verifyPayment/", verify_payment, name="verify_payment"),
    path("orderHistory/", order_history, name="order_history"), # this will retun all orders of a user
    path("orderHistoryItems/<int:order_id>/", order_history_items, name="order_history_items"), # this will retun all orders of a user`
    path('return/<int:order_id>/', request_return, name='request-return'),
    
    path('userOrders/<int:customer_id>/', user_orders, name='user_orders'),  # Need to be ckeck whos is using it

    path('applyCoupon/', validate_coupon, name='validate_coupon'),

    path('invoice/<int:order_id>/', OrderInvoicePDFView.as_view(), name='order-invoice-pdf'),
    
    #test
    # path("create-order/", create_order, name="create_order"),
    
]