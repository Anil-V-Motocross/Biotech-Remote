from django.contrib import admin
from .models import Shipment, Webhook, DeliveryLocation


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'carrier', 'shipment_status', 'pickup_date', 'last_updated')
    search_fields = ('order__order_id', 'carrier', 'shipment_status')
    list_filter = ('shipment_status', 'carrier', 'pickup_date', 'last_updated')
    readonly_fields = ('last_updated',)  # Prevent manual editing of auto-updated fields

@admin.register(Webhook)
class WebhookAdmin(admin.ModelAdmin):
    list_display = ('id', 'url', 'events', 'is_active', 'created_at', 'updated_at')
    search_fields = ('url', 'events')
    list_filter = ('is_active',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DeliveryLocation)
class DeliveryLocationAdmin(admin.ModelAdmin):
    list_display = ('pincode', 'city', 'state', 'created_at')
    search_fields = ('pincode',)
    ordering = ('-created_at',)

