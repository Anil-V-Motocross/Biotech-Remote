from django.contrib import admin
from .models import Order, OrderItem, Cart, Wishlist, DeliveryAddress, OrderStatus

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'grand_total', 'date', 'customer_id', 'customer_name', 'email', 'mobile', 'tracking_id', 'payment_method', 'delivery_option', 'status', 'razorpay_order_id')
    
@admin.register(OrderStatus)
class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'timestamp', 'notes')
    list_filter = ('status',)
    search_fields = ('order__order_id', 'status', 'notes')


class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'product_id', 'quantity', 'mrp', 'total')

class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'product_id', 'quantity')
    
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'product_id')
    
class DeliveryAddressAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'order_id', 'first_name', 'last_name', 'state', 'city', 'pincode')

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(DeliveryAddress, DeliveryAddressAdmin)