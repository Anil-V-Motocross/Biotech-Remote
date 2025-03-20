from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Coupon, CouponUsage

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'get_categories', 'get_products', 'is_first_order', 
                    'start_date', 'end_date', 'minimum_order_value', 'active')
    search_fields = ('code', 'description')
    list_filter = ('discount_type', 'active', 'start_date', 'end_date')
    filter_horizontal = ('applicable_categories', 'applicable_products')
    readonly_fields = ('used_count',)

    def get_categories(self, obj):
        return ", ".join([category.name for category in obj.applicable_categories.all()])
    get_categories.short_description = "Applicable Categories"

    def get_products(self, obj):
        return ", ".join([product.name for product in obj.applicable_products.all()])
    get_products.short_description = "Applicable Products"

@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'coupon', 'usage_count', 'used_at')
    search_fields = ('user__username', 'coupon__code')
    list_filter = ('used_at',)

