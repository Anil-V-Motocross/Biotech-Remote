from django.db import models
from order.models import Order

# class Shipment(models.Model):
#     order_id = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="shipment")
#     carrier = models.CharField(max_length=100)  # Eg, Delivery, Bluedart
#     tracking_id = models.CharField(max_length=50)
#     shipment_status = models.CharField(max_length=100)  # Eg, Shipped, In Transit, Delivered
#     estimated_delivery_date = models.DateField(null=True, blank=True)
#     last_updated = models.DateTimeField(auto_now=True)

#     def __str__(self):
#         return f"Shipment for Order {self.order.order_id} - {self.tracking_id}"



class Shipment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="shipment")
    carrier = models.CharField(max_length=100)  # Example: Bluedart
    shipment_status = models.CharField(max_length=100, default="Pending")  # Example: Shipped, In Transit, Delivered
    shipment_status_code = models.CharField(max_length=10, null=True, blank=True)  # Example: 'NFI'
    from_location = models.CharField(max_length=255, null=True, blank=True)
    to_location = models.CharField(max_length=255, null=True, blank=True)
    order_data = models.TextField(null=True, blank=True)  # Additional order details
    pickup_date = models.DateTimeField(null=True, blank=True)
    tracking_url = models.URLField(max_length=500, null=True, blank=True)  # Shipway tracking URL
    last_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Shipment for Order {self.order.order_id} - {self.order.tracking_id}"

class Webhook(models.Model):
    url = models.URLField(max_length=500, unique=True)  # Increased max length
    events = models.CharField(max_length=255)  # Stores subscribed events
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Webhook ({'Active' if self.is_active else 'Inactive'}) - {self.url}"


class DeliveryLocation(models.Model):
    pincode = models.CharField(max_length=6, unique=True)
    city = models.CharField(max_length=500, blank=True)
    state = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        
        return self.pincode