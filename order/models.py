from django.db import models
from product.models import Product
from account.models import User
from django.core.files.base import ContentFile
import os
from combo.models import ComboOffer

# Create your models here.

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

    delivery_option_types=[
        ('Standard', 'Standard'),
        ('Express', 'Express'),
    ]
    delivery_option = models.CharField(max_length=10, choices=delivery_option_types, default='Standard')

    payment_method_types=[
        ('Cash', 'Cash'),
        ('UPI', 'UPI'),
    ]
    payment_method = models.CharField(max_length=10, choices=payment_method_types, null=True, blank=True)

    status = models.CharField(max_length=50)
    razorpay_order_id = models.CharField(max_length=50, null=True, blank=True)

    # Track if order is a combo purchase
    is_combo_purchase = models.BooleanField(default=False)  

    # Coupon-related fields
    coupon_applied = models.BooleanField(default=False)  # Whether a coupon was used
    applied_coupon = models.ForeignKey('coupon.Coupon', on_delete=models.SET_NULL, null=True, blank=True)  # Applied coupon
    coupon_discount = models.FloatField(default=0)

    def __str__(self):
        return str(self.id)
    
class OrderItem(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    combo_offer = models.ForeignKey(ComboOffer, on_delete=models.SET_NULL, null=True, blank=True)  # Track combo purchases
    sku = models.CharField(max_length=40)
    image = models.ImageField(upload_to='order_items/', blank=True, null=True)
    quantity = models.IntegerField(default=0)
    price = models.FloatField(default=0)
    sale_price = models.FloatField(default=0)
    discount = models.FloatField(db_default=0)
    total = models.FloatField(default=0)

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