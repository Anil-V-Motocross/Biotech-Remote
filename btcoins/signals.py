from django.db.models.signals import post_save
from django.dispatch import receiver
from django.conf import settings
from .models import BTCoinsWallet, BTCoinsSettings, BTCoinsTransaction
from order.models import OrderStatus

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_btcoins_wallet(sender, instance, created, **kwargs):
    if created:
        BTCoinsWallet.objects.create(user=instance)

@receiver(post_save, sender=OrderStatus)
def credit_coins_after_delivery(sender, instance, created, **kwargs):
    """Credits coins only if all required statuses exist before marking order as DELIVERED"""
    
    if instance.status == 'DELIVERED':  
        order = instance.order
        user = order.customer_id  

        print(f"Order Delivered: {order.order_id} | User: {user}")

        if not user:
            print("No user found for this order. Exiting...")
            return  # Safety check

        # Check if order was already delivered before
        if OrderStatus.objects.filter(order=order, status='DELIVERED').exclude(id=instance.id).exists():
            print("Order is already marked as delivered. No coins will be credited.")
            return

        # Required statuses before crediting coins
        required_statuses = {
            'INITIATED', 'PROCESSING', 'ORDER_CONFIRMED', 'DISPATCHED',
            'ON_THE_WAY', 'OUT_FOR_DELIVERY'
        }

        # Fetch the actual statuses recorded for this order
        actual_statuses = set(OrderStatus.objects.filter(order=order).values_list('status', flat=True))

        print(f"Actual Statuses: {actual_statuses}")

        # Check if all required statuses are present
        if not required_statuses.issubset(actual_statuses):
            print("Not all required statuses exist. Coins will NOT be credited.")
            return  # Prevent double crediting due to admin mistakes

        print("All required statuses verified. Proceeding with coin credit...")

        # Fetch wallet or create if it doesn't exist
        wallet, _ = BTCoinsWallet.objects.get_or_create(user=user)
        print(f"User Wallet Found: {wallet} | Total Coins Before: {wallet.total_coins}")

        # Retrieve global coin settings
        settings = BTCoinsSettings.get_settings()
        print(f"Max Earnable Coins Per Order: {settings.max_coins_earned_per_order}")

        # Calculate coins based on grand total (10 coins per 100 rupees)
        coins_to_credit = (order.grand_total // 100) * 10
        print(f"Calculated Coins to Credit: {coins_to_credit}")

        # Apply max earning limit
        max_earnable = settings.max_coins_earned_per_order
        coins_to_credit = min(coins_to_credit, max_earnable)

        print(f"Coins After Applying Limit: {coins_to_credit}")

        if coins_to_credit > 0:
            # Add coins to the user's wallet
            wallet.total_coins += coins_to_credit
            wallet.save()
            print(f"Updated Wallet Balance: {wallet.total_coins}")

            # Ensure a transaction entry is created
            transaction, created = BTCoinsTransaction.objects.get_or_create(
                user=user,
                order=order,
                defaults={
                    'transaction_type': 'EARN',
                    'coins': coins_to_credit,
                    'reference': f"Coins earned from order #{order.order_id}"
                }
            )

            if created:
                print(f"Transaction Created: {transaction}")
            else:
                print("Transaction already exists for this order.")

        else:
            print("No coins credited due to earning limits.")

