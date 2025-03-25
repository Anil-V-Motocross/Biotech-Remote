from django.contrib import admin
from .models import BTCoinsWallet, BTCoinsTransaction, Referral, BTCoinsSettings

@admin.register(BTCoinsWallet)
class BTCoinsWalletAdmin(admin.ModelAdmin):
    list_display = ("id","user", "total_coins", "referral_code", "referral_used_count")
    search_fields = ("user__first_name", "referral_code")
    readonly_fields = ("referral_code",) 

@admin.register(BTCoinsTransaction)
class BTCoinsTransactionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "transaction_type", "reference", "coins", "created_at", "expires_at")
    list_filter = ("transaction_type", "created_at")
    search_fields = ("user__first_name", "reference")

@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ("id", "referrer", "referred_user", "created_at")
    search_fields = ("referrer__first_name", "referred_user__first_name")

@admin.register(BTCoinsSettings)
class BTCoinsSettingsAdmin(admin.ModelAdmin):
    list_display =("id", "referral_limit", "referral_coins_referrer", "referral_coins_referred",
                   "max_coins_earned_per_order", "max_coins_redeemed_per_order", "coin_expiry_days"
                   )