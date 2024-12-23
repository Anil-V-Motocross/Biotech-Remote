from django.contrib import admin
from .models import Order

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'date', 'product_id', 'customer_id', 'customer_name', 'email', 'mobile', 'address', 'tracking_id', 'payment_method', 'status')


admin.site.register(Order, OrderAdmin)