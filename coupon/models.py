from django.db import models
from product.models import ProductCategory, MainProduct
from category.models import Category
from account.models import User
from django.utils import timezone
import random, string
from order.models import Order
from django.core.exceptions import ValidationError
from django.db.models import Sum

# === PAYMENT METHOD MODEL ===
# class PaymentMethod(models.Model):
#     name = models.CharField(max_length=50, unique=True)  # e.g., 'Cash', 'UPI'

#     def __str__(self):
#         return self.name


# # === ORDER PAYMENT METHOD MODEL ===
# class OrderPaymentMethod(models.Model):
#     order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="payment_methods")
#     payment_method = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE)

#     def __str__(self):
#         return f"Order {self.order.order_id} - {self.payment_method.name}"



def generate_unique_coupon_code(length=8):
    """Generate a unique coupon code with at least 4 numbers and a 'BM-' prefix."""
    prefix = "BM"
    num_length = 4  
    total_length = length - len(prefix) 

    while True:
        # Generate at least 4 digits
        digits = random.choices(string.digits, k=num_length)
        # Fill the rest with random uppercase letters
        letters = random.choices(string.ascii_uppercase, k=total_length - num_length)

        # Combine and shuffle
        code_chars = digits + letters
        random.shuffle(code_chars)

        # Final coupon code
        coupon_code = prefix + ''.join(code_chars)

        # Ensure uniqueness
        if not Coupon.objects.filter(code=coupon_code).exists():
            return coupon_code

class Coupon(models.Model):
    DISCOUNT_TYPES = (
        ('PERCENTAGE', 'Percentage'),
        ('FLAT', 'Flat Amount'),
    )

    code = models.CharField(max_length=20, unique=True, blank=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    max_discount_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)  
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(blank=True, null=True)
    used_count = models.PositiveIntegerField(default=0)
    minimum_order_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    active = models.BooleanField(default=True)
    
    applicable_categories = models.ManyToManyField(Category, blank=True)
    applicable_products = models.ManyToManyField(MainProduct, blank=True) 
    # applicable_users = models.ManyToManyField(User, blank=True) #Restrict the coupon to specific users (VIP customers, first-time users, etc.).
    # allowed_payment_methods = models.ManyToManyField(PaymentMethod, blank=True)
    # applicable_user_groups = models.ManyToManyField(Group, blank=True)  
    is_first_order = models.BooleanField(default=False)  
    is_stackable = models.BooleanField(default=False)  #Allows the coupon to be combined with other discounts.
    redemption_message = models.TextField(blank=True, null=True) #Custom message displayed to users after successful coupon application.

    user_limit = models.PositiveIntegerField(default=1)

    def save(self, *args, **kwargs):
        """Generate a unique coupon code if not provided."""
        if not self.code:
            self.code = generate_unique_coupon_code()

        # Ensure percentage discount doesn't exceed max discount value
        if self.discount_type == 'PERCENTAGE' and self.max_discount_value is not None:
            if self.discount_value > 100:
                raise ValidationError("Percentage discount cannot be more than 100%.")

        super().save(*args, **kwargs)

    def apply_discount(self, order_total):
        """Apply discount while considering max discount cap (if applicable)."""
        if self.discount_type == 'PERCENTAGE':
            discount = (self.discount_value / 100) * order_total
            if self.max_discount_value:  # Apply cap if set
                discount = min(discount, self.max_discount_value)
            return discount
        return self.discount_value

    def is_valid(self, user, order_total):
        """Check if the coupon is valid, considering date, usage limits, and user limit."""     
        if not self.active or not (self.start_date <= timezone.now() <= self.end_date):
            return False
        
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        
        if CouponUsage.usage_count_for_user(user, self) >= self.user_limit:
            return False
        if self.minimum_order_value and order_total < self.minimum_order_value:
            return False
        if self.is_first_order and user.orders.count() > 0:  # Ensure it's a first-time order
            return False
        return True

    def increment_usage(self):
        """Increase the usage count when a coupon is used."""
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            raise ValueError("Coupon usage limit reached.")
        self.used_count += 1
        self.save()

    def __str__(self):
        return self.code


class CouponUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='user_usages')
    used_at = models.DateTimeField(auto_now_add=True)
    usage_count = models.PositiveIntegerField(default=1)


    class Meta:
        unique_together = ('user', 'coupon')  # Prevent the same user from using the same coupon more than once

    @classmethod
    def usage_count_for_user(cls, user, coupon):
        """Get the count of times a user has used a specific coupon."""
        return cls.objects.filter(user=user, coupon=coupon).aggregate(total_usage=Sum('usage_count'))['total_usage'] or 0
    def __str__(self):
        return f"{self.user} used {self.coupon.code} on {self.used_at}"