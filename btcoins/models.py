from django.db import models
from account.models import User
from order.models import Order
import random
import string
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

class BTCoinsSettings(models.Model):
    """Global settings for BTCoins wallet"""
    referral_limit = models.PositiveIntegerField(default=10) 
    referral_coins_referrer = models.PositiveIntegerField(default=200)  # Coins for referrer
    referral_coins_referred = models.PositiveIntegerField(default=50)  # Coins for referred user
    max_coins_earned_per_order = models.PositiveIntegerField(default=100)  # Max coins user can earn per order
    max_coins_redeemed_per_order = models.PositiveIntegerField(default=200)  
    coin_expiry_days = models.PositiveIntegerField(default=365)  
    coins_per_100_rupees = models.PositiveIntegerField(default=10)

    def __str__(self):
        return "BTCoins Global Settings"

    @classmethod
    def get_settings(cls):
        """Fetch settings, creating default if none exist"""
        settings, created = cls.objects.get_or_create(id=1)
        return settings

class BTCoinsWallet(models.Model):
    """ User's coin wallet """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="btcoins_wallet")
    total_coins = models.PositiveIntegerField(default=0)  
    referral_used_count = models.PositiveIntegerField(default=0)  
    referral_code = models.CharField(max_length=15, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.referral_code:
            self.referral_code = self.generate_unique_referral_code()
        super().save(*args, **kwargs)

    @staticmethod
    def generate_unique_referral_code():
        """Generate a unique 10-character referral code"""
        while True:
            code = "BMURC" + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
            if not BTCoinsWallet.objects.filter(referral_code=code).exists():
                return code


    def add_coins(self, coins, order=None):
        """ Add coins to the wallet, but limit max earned per order """
        settings = BTCoinsSettings.get_settings()
        max_earn = settings.max_coins_earned_per_order

        # Enforce max coins per order
        coins_to_add = min(coins, max_earn)
        self.total_coins += coins_to_add
        self.save()

        # Log the transaction
        BTCoinsTransaction.objects.create(
            user=self.user,
            order=order,
            coins=coins_to_add,
            transaction_type="EARN",
            reference=f"Order #{order.id}" if order else "Bonus",
            expires_at=timezone.now() + timedelta(days=settings.coin_expiry_days),
        )
        return coins_to_add

    def redeem_coins(self, coins, order):
        """ Redeem coins for an order, enforcing redemption limit """
        settings = BTCoinsSettings.get_settings()
        max_redeem = settings.max_coins_redeemed_per_order

        if coins > self.total_coins:
            raise ValueError("Not enough coins to redeem.")

        # Apply max redemption limit
        coins_to_redeem = min(coins, max_redeem)
        self.total_coins -= coins_to_redeem
        self.save()

        # Log the transaction
        BTCoinsTransaction.objects.create(
            user=self.user,
            order=order,
            coins=coins_to_redeem,
            transaction_type="REDEEM",
            reference=f"Order #{order.id}",
        )
        return coins_to_redeem

    def __str__(self):
        return f"{self.user.first_name} - {self.total_coins} Coins"
    
class BTCoinsTransaction(models.Model):
    """ Records transactions in the wallet """
    TRANSACTION_TYPES = [
        ("EARN", "Earn"),  # Earned coins (e.g., purchase, referral)
        ("REDEEM", "Redeem"),  # Redeemed coins (e.g., discount)
        ("EXPIRE", "Expire"),  # Expired coins
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="btcoins_transactions")
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    coins = models.PositiveIntegerField()  
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    reference = models.CharField(max_length=255, blank=True, null=True)  # Order ID, Referral Code, etc.
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # Expiry date for earned coins
    notified = models.BooleanField(default=False)  # To track if the user was notified about expiry

    def save(self, *args, **kwargs):
        """ Automatically set expires_at for earned coins """
        if self.transaction_type == "EARN" and not self.expires_at:
            settings = BTCoinsSettings.get_settings()
            self.expires_at = timezone.now() + timedelta(days=settings.coin_expiry_days)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.first_name} - {self.transaction_type} - {self.coins} Coins"

    @staticmethod
    def redeem_coins(user, order, coins_to_redeem):
        """Apply coin limit per order and redeem coins"""
        settings = BTCoinsSettings.get_settings()
        max_redeemable = min(settings.max_coins_redeemed_per_order, coins_to_redeem)

        wallet = user.btcoins_wallet
        if wallet.total_coins >= max_redeemable:
            wallet.total_coins -= max_redeemable
            wallet.save()

            BTCoinsTransaction.objects.create(
                user=user,
                order=order,
                coins=max_redeemable,
                transaction_type="REDEEM",
                reference=f"Order {order.id}"
            )
            return max_redeemable
        return 0

class Referral(models.Model):
    """ Referral system to reward users """
    referrer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="btcoins_referred_users")
    referred_user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="btcoins_referral")
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        """Ensure referral limit is not exceeded and allocate coins"""
        print(f"Creating referral: {self.referrer.id} → {self.referred_user.id}")
        settings = BTCoinsSettings.get_settings()
        referrer_wallet = self.referrer.btcoins_wallet

        if referrer_wallet.referral_used_count < settings.referral_limit:
            print(f"Before adding coins: Referrer Wallet Coins: {referrer_wallet.total_coins}")

            # Directly update total_coins to avoid duplicate transactions
            referrer_wallet.total_coins += settings.referral_coins_referrer
            referrer_wallet.referral_used_count += 1
            referrer_wallet.save(update_fields=['total_coins', 'referral_used_count'])

            referred_wallet = self.referred_user.btcoins_wallet
            referred_wallet.total_coins += settings.referral_coins_referred
            referred_wallet.save(update_fields=['total_coins'])

            print(f"After adding coins: Referrer Wallet Coins: {referrer_wallet.total_coins}")

        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.referrer.first_name} → {self.referred_user.first_name}"
