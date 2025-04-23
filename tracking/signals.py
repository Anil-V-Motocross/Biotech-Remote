# orders/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from order.models import OrderStatus
from tracking.views import push_order_to_shipway, push_return_order_to_shipway
from tracking.view.send_sms_to_user import send_order_confirmation_sms_to_admin
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

    order = instance.order
    status = instance.status
    if created and instance.status == 'ORDER_CONFIRMED':

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
                send_order_confirmation_sms_to_admin(order, status)
            except Exception as e:
                print(f"[ERROR] Failed to push to Shipway: {e}")
        else:
            print(f"[INFO] Cannot push to Shipway: Missing INITIATED or PROCESSING status.")

    elif created and instance.status == 'READY_FOR_PICKUP':
        try:
            send_order_confirmation_sms_to_admin(order, status)
        except Exception as e:
            print(f"[ERROR] Failed to send sms to the user: {e}")

    elif created and instance.status == 'RETURN_APPROVED':
        order = instance.order

        print(f"[DEBUG] Checking required previous statuses for Order ID: {order.order_id}")

        required_statuses = {'INITIATED', 'PROCESSING', 'ORDER_CONFIRMED', 'DISPATCHED', 'ON_THE_WAY', 'OUT_FOR_DELIVERY', 'DELIVERED', 'RETURN_REQUESTED'}
        existing_statuses = set(
            OrderStatus.objects.filter(order=order).values_list('status', flat=True)
        )

        print(f"[DEBUG] Existing statuses for Order {order.order_id}: {existing_statuses}")

        if required_statuses.issubset(existing_statuses):
            print(f"[DEBUG] All required statuses present. Proceeding to push to Shipway.")
            try:
                push_return_order_to_shipway(order_id=order.order_id)
            except Exception as e:
                print(f"[ERROR] Failed to push to Shipway: {e}")
        else:
            print(f"[INFO] Cannot push to Shipway: Missing INITIATED or PROCESSING status.")            