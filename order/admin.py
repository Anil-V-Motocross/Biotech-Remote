from django.contrib import admin
from .models import Order, OrderItem, Cart, Wishlist, DeliveryAddress, OrderStatus


class OrderStatusInline(admin.TabularInline):  # Display order status inline
    model = OrderStatus
    extra = 1  
    readonly_fields = ('timestamp',)  
    fields = ('status', 'timestamp', 'notes') 

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'latest_status', 'grand_total', 'date', 'customer_id', 'customer_name', 'email', 'mobile', 'tracking_id', 'payment_method', 'delivery_option', 'razorpay_order_id')
    inlines = [OrderStatusInline] 
    
    def latest_status(self, obj):
        """ Get the latest status for an order. """
        latest_status = obj.status_history.order_by('-timestamp').first()  # Use status_history instead of orderstatus_set
        return latest_status.status if latest_status else "No Status"

    latest_status.short_description = "Latest Status" 

class OrderStatusAdmin(admin.ModelAdmin):
    list_display = ('order', 'status', 'timestamp', 'notes')
    list_filter = ('status', 'timestamp')
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
admin.site.register(OrderStatus, OrderStatusAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Wishlist, WishlistAdmin)
admin.site.register(DeliveryAddress, DeliveryAddressAdmin)