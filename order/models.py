from django.db import models
from product.models import Product
from account.models import User

# Create your models here.

class Order(models.Model):
    order_id = models.CharField(max_length=50, default=0)
    date = models.DateField()
    
    customer_id = models.ForeignKey(User, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=50)
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
    quantity = models.IntegerField()
    price = models.FloatField()
    total = models.FloatField()
    

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