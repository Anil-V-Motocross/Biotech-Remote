from django.urls import path
from .view.getOrderDetails import get_order_details 
from .view.addWebhook import add_webhook
from .view.deleteWebhook import delete_webhook
from .view.callBackApi import shipway_webhook

urlpatterns = [
    path('test-authenticate/', delete_webhook, name='test_authenticate_user'),
    path("webhook/shipway/", shipway_webhook, name="shipway-webhook"),
]