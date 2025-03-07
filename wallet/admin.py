from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Wallet, Transaction

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance", "is_active", "created_at", "updated_at")
    search_fields = ("user__username",)
    list_filter = ("is_active",)
    readonly_fields = ("created_at", "updated_at")

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("wallet", "transaction_type", "amount", "created_at")
    search_fields = ("wallet__user__username", "transaction_type")
    list_filter = ("transaction_type", "created_at")
    readonly_fields = ("created_at",)
