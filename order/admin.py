from django.contrib import admin
from .models import Order, Cart

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'date', 'product_id', 'customer_id', 'customer_name', 'email', 'mobile', 'address', 'tracking_id', 'payment_method', 'status')

class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'product_id', 'quantity')

admin.site.register(Order, OrderAdmin)
admin.site.register(Cart, CartAdmin)