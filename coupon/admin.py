from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Coupon, CouponUsage

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('id', 'code', 'discount_type', 'discount_value', 'max_discount_value', 'start_date', 'end_date', 'usage_limit', 'used_count', 'active')
    search_fields = ('code', 'description')
    list_filter = ('discount_type', 'active', 'start_date', 'end_date')
    filter_horizontal = ('applicable_categories', 'applicable_products')
    readonly_fields = ('used_count',)
    
@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'coupon', 'used_at')
    search_fields = ('user__username', 'coupon__code')
    list_filter = ('used_at',)

