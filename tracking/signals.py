# orders/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from order.models import OrderStatus
from tracking.views import push_order_to_shipway
from django.http import HttpRequest
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

from django.conf import settings

@receiver(post_save, sender=OrderStatus)
def push_order_when_confirmed(sender, instance, created, **kwargs):
    """
    Push order to Shipway only if status is ORDER_CONFIRMED
    AND previous statuses INITIATED and PROCESSING exist.
    """
    print(f"[DEBUG] Signal triggered for OrderStatus ID: {instance.id}, Status: {instance.status}")

    if created and instance.status == 'ORDER_CONFIRMED':
        order = instance.order

        print(f"[DEBUG] Checking required previous statuses for Order ID: {order.order_id}")

        required_statuses = {'INITIATED', 'PROCESSING'}
        existing_statuses = set(
            OrderStatus.objects.filter(order=order).values_list('status', flat=True)
        )

        print(f"[DEBUG] Existing statuses for Order {order.order_id}: {existing_statuses}")

        if required_statuses.issubset(existing_statuses):
            print(f"[DEBUG] All required statuses present. Proceeding to push to Shipway.")
            try:
                push_order_to_shipway(order_id=order.order_id)
            except Exception as e:
                print(f"[ERROR] Failed to push to Shipway: {e}")
        else:
            print(f"[INFO] Cannot push to Shipway: Missing INITIATED or PROCESSING status.")