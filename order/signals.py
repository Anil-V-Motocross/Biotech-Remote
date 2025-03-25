from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Order, OrderStatus


@receiver(post_save, sender=Order)
def create_order_status(sender, instance, created, **kwargs):
    """ Automatically create an initial OrderStatus when a new Order is created """
    if created:  # Only run when a new order is created
        OrderStatus.objects.create(order=instance, status='INITIATED')    