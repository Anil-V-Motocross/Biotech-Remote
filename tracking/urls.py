from django.urls import path
from .views import get_shipway_order_by_id, cancel_shipway_orders

urlpatterns = [
    # path('test-authenticate/', get_order_details, name='test_authenticate_user'),
    # path("webhook/shipway/", add_webhook, name="shipway-webhook"),
    # path("webhook/callback/", shipway_webhook, name="shipway-webhook"),
    path('shipway/order/<str:order_id>/', get_shipway_order_by_id, name='get_shipway_order'),
    path('shipway/cancel-orders/', cancel_shipway_orders, name='cancel_shipway_orders'),
]