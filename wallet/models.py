from django.db import models
import uuid
from account.models import User
from django.db import models, transaction

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="wallet")
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Wallet"
        verbose_name_plural = "Wallets"

    def __str__(self):
        return f"{self.user.email} - Balance: ₹{self.balance}"

    def credit(self, amount):
        """Safely add money to the wallet"""
        with transaction.atomic():
            self.balance += amount
            self.save()

    def debit(self, amount):
        """Safely deduct money from the wallet"""
        if amount > self.balance:
            raise ValueError("Insufficient balance")
        with transaction.atomic():
            self.balance -= amount
            self.save()

    def has_sufficient_balance(self, amount):
        """Check if the wallet has enough balance"""
        return self.balance >= amount


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("CREDIT", "Credit"),
        ("DEBIT", "Debit"),
        ("REFUND", "Refund"),
        ("WITHDRAW", "Withdraw"),
    ]

    TRANSACTION_STATUS = [
        ("PENDING", "Pending"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
        ("CANCELLED", "Cancelled"),
        ("REVERSED", "Reversed"),
    ]

    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name="transactions")
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=TRANSACTION_STATUS, default="PENDING")
    reference_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Transaction"
        verbose_name_plural = "Transactions"
        ordering = ["-created_at"]

        def __str__(self):
            return f"{self.wallet.user.email} - {self.transaction_type} - ₹{self.amount} - {self.status}"
