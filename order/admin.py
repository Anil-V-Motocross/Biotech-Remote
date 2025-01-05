from django.contrib import admin
from .models import Order, OrderItem, Cart, Wishlist

# Register your models here.
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'grand_total', 'date', 'customer_id', 'customer_name', 'email', 'mobile', 'address', 'tracking_id', 'payment_method', 'status')
    

class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'order_id', 'product_id', 'quantity', 'price', 'total')

class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'product_id', 'quantity')
    
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('id', 'user_id', 'product_id')

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Wishlist, WishlistAdmin)