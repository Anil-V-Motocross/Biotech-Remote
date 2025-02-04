from django.db import models
from product.models import Product
from account.models import User
from django.core.files.base import ContentFile
import os

# Create your models here.

class Order(models.Model):
    order_id = models.CharField(max_length=50, default=0)
    date = models.DateField()
    
    customer_id = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=50)
    total_price = models.FloatField(default=0)
    total_discount = models.FloatField(default=0)
    grand_total = models.FloatField(default=0)
    email = models.EmailField()
    mobile = models.CharField(max_length=15)
    address = models.CharField(max_length=200, null=True, blank=True)
    tracking_id = models.CharField(max_length=50)
    payment_method = models.CharField(max_length=50)
    status = models.CharField(max_length=50)

    def __str__(self):
        return str(self.id)
    
class OrderItem(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.ForeignKey(Product, on_delete=models.CASCADE)
    sku = models.CharField(max_length=40)
    image = models.ImageField(upload_to='order_items/', blank=True, null=True)
    quantity = models.IntegerField(default=0)
    price = models.FloatField(default=0)
    sale_price = models.FloatField(default=0)
    discount = models.FloatField(db_default=0)
    total = models.FloatField(default=0)
    
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