from django.db import models
from product.models import ProductCategory, MainProduct, Product
from account.models import User
from django.utils import timezone
# Create your models here.

class Coupon(models.Model):
    DISCOUNT_TYPES = (
        ('PERCENTAGE', 'Percentage'),
        ('FLAT', 'Flat Amount'),
    )

    code = models.CharField(max_length=20, unique=True)
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    usage_limit = models.PositiveIntegerField(blank=True, null=True)
    used_count = models.PositiveIntegerField(default=0)
    minimum_order_value = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    active = models.BooleanField(default=True)
    
    applicable_categories = models.ManyToManyField(ProductCategory, blank=True)
    applicable_products = models.ManyToManyField(MainProduct, blank=True)
    # applicable_plants_and_seeds = models.ManyToManyField(Product, blank=True)
    user_limit = models.PositiveIntegerField(default=1)

    def apply_discount(self, order_total):
        """Apply the discount based on the type (percentage or flat)."""
        if self.discount_type == 'PERCENTAGE':
            return (self.discount_value / 100) * order_total
        else:  # Flat discount
            return self.discount_value

    def is_valid(self):
        """Check if the coupon is valid, considering date, usage limits, and user limit."""     
        if not self.active or not (self.start_date <= timezone.now() <= self.end_date):
            return False
        
        if self.usage_limit and self.used_count >= self.usage_limit:
            return False
        
        user_usage_count = CouponUsage.usage_count_for_user(user, self)
        if user_usage_count >= self.user_limit:
            return False
        
        return True

    def increment_usage(self):
        """Increase the usage count when a coupon is used."""
        if self.usage_limit is not None and self.used_count >= self.usage_limit:
            raise ValueError("Coupon usage limit reached.")
        self.used_count += 1
        self.save()

    # def save(self, *args, **kwargs):
    #     if self.usage_limit is not None and self.used_count > self.usage_limit:
    #         raise ValueError("Coupon usage limit reached.")
    #     super(Coupon, self).save(*args, **kwargs)

    def _str_(self):
        return self.code


class CouponUsage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='coupon_usages')
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='user_usages')
    used_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        unique_together = ('user', 'coupon')  # Prevent the same user from using the same coupon more than once

    @classmethod
    def usage_count_for_user(cls, user, coupon):
        """Get the count of times a user has used a specific coupon."""
        return cls.objects.filter(user=user, coupon=coupon).count()  # Count the number of times a user has used a coupon
    
    def _str_(self):
        return f"{self.user} used {self.coupon.code} on {self.used_at}"