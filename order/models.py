from django.db import models
from product.models import Product
from account.models import User
from django.core.files.base import ContentFile
import os
from combo.models import ComboOffer
from decimal import Decimal
from django.utils import timezone
from datetime import timedelta


class Order(models.Model):
    order_id = models.CharField(max_length=50, default=0)
    date = models.DateField()
    
    customer_id = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=50)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)

    total_price = models.FloatField(default=0)
    total_discount = models.FloatField(default=0)
    grand_total = models.FloatField(default=0)

    tracking_id = models.CharField(max_length=50, null=True, blank=True)

    DELIVERY_OPTIONS = [
        ('Standard', 'Standard'),
        ('Express', 'Express'),
        ('PickUpStore', 'Pick Up Store'),
    ]
    delivery_option = models.CharField(max_length=15, choices=DELIVERY_OPTIONS, default='Standard')

    payment_method_types=[
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
    ]
    payment_method = models.CharField(max_length=10, choices=payment_method_types, null=True, blank=True)

    # ✅ Store reference (Only if PickUpStore is selected)
    store_id = models.ForeignKey('store.Store', on_delete=models.SET_NULL, null=True, blank=True)

    # ✅ Pickup deadline (only if PickUpStore is chosen)
    pickup_deadline = models.DateTimeField(null=True, blank=True)
    

    # status = models.CharField(max_length=50)
    razorpay_order_id = models.CharField(max_length=50, null=True, blank=True)

    # Track if order is a combo purchase
    is_combo_purchase = models.BooleanField(default=False)  

    # Coupon-related fields
    coupon_applied = models.BooleanField(default=False)  # Whether a coupon was used
    applied_coupon = models.ForeignKey('coupon.Coupon', on_delete=models.SET_NULL, null=True, blank=True)  # Applied coupon
    coupon_discount = models.FloatField(default=0)

    def save(self, *args, **kwargs):
        """
        Auto-set pickup deadline if the user selects 'Pick Up Store'.
        """
        if self.delivery_option == 'PickUpStore' and not self.pickup_deadline:
            self.pickup_deadline = timezone.now() + timedelta(days=7)  # 7 days from now
        elif self.delivery_option != 'PickUpStore':  
            self.pickup_deadline = None  # Reset if delivery option changes
        super().save(*args, **kwargs)

    def __str__(self):
        return str(self.id)

class OrderStatus(models.Model):
    STATUS_CHOICES = [
        ('INITIATED', 'Initiated'),
        ('PROCESSING', 'Processing'),
        ('ORDER_CONFIRMED', 'Order Confirmed'),
        ('READY_FOR_PICKUP', 'Ready for Pickup'),  
        ('PICKUP_COMPLETED', 'Pickup Completed'),  
        ('DISPATCHED', 'Dispatched'),
        ('ON_THE_WAY', 'On the Way'),
        ('OUT_FOR_DELIVERY', 'Out for Delivery'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
        ('RETURN_REQUESTED', 'Return Requested'),
        ('RETURN_APPROVED', 'Return Approved'),
        ('RETURN_REJECTED', 'Return Rejected'),
        ('RETURNED', 'Returned'),
        ('PICKUP_EXPIRED', 'Pickup Expired'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='INITIATED')
    timestamp = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True, null=True)  # Optional: Track reasons (e.g., "Customer requested return")

    def __str__(self):
        return f"{self.order.order_id} - {self.get_status_display()} at {self.timestamp}"

    class Meta:
        ordering = ['-timestamp']


class OrderItem(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    combo_offer = models.ForeignKey(ComboOffer, on_delete=models.SET_NULL, null=True, blank=True)  # Track combo purchases
    sku = models.CharField(max_length=40)
    image = models.ImageField(upload_to='order_items/', blank=True, null=True)
    quantity = models.IntegerField(default=0)

    mrp = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))
    total = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal("0.00"))

    hsn_code = models.CharField(max_length=10, blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if self.product_id and not self.image:  # Only copy if image is not already set
            product_image = self.product_id.image
            if product_image:
                self.image.save(
                    os.path.basename(product_image.name),  # Copy the same filename
                    ContentFile(product_image.read()),  # Read the content
                    save=False  # Don't save the model yet
                )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.product_id.name} - {self.id}"

class Cart(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.product_id.name} - {self.quantity}"
    

class Wishlist(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product_id.name}"
    
class DeliveryAddress(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField(max_length=200)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    pincode = models.IntegerField()
    address_types=[
        ('Home', 'Home'),
        ('Work', 'Work'),
    ]
    address_type = models.CharField(max_length=255,choices=address_types)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name="delivery_user_addresses")
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_address", default='0')

    def __str__(self):
        return f"{self.user_id}, {self.city}, {self.state}, {self.pincode}"