from django.urls import path
from .view.getOrderDetails import get_order_details 
from .view.addWebhook import add_webhook
from .view.deleteWebhook import delete_webhook
from .view.callBackApi import shipway_webhook
from .view.carriersList import carriers_list
from .view.pushOrderData import push_order_data

urlpatterns = [
    path('test-authenticate/', get_order_details, name='test_authenticate_user'),
    path("webhook/shipway/", add_webhook, name="shipway-webhook"),
    path("webhook/callback/", shipway_webhook, name="shipway-webhook"),

]