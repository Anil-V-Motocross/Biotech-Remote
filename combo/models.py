from django.db import models
from product.models import Product
from django.dispatch import receiver
from django.db.models.signals import m2m_changed


class ComboOffer(models.Model):
    title = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='combo_images/', default='default/combo_default.jpg')
    products = models.ManyToManyField(Product, related_name='combo_offers')

    # These fields are automatically calculated (no user input)
    total_price = models.FloatField(null=True, blank=True)  # Allow NULL values
    discount = models.FloatField(default=0)  # User provides discount
    final_price = models.FloatField(null=True, blank=True)  # Allow NULL values

    is_shop_the_look = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def calculate_prices(self):
        """Calculate total and final prices dynamically."""
        total_price = sum(product.price for product in self.products.all())  # Sum product prices
        final_price = total_price - self.discount if self.discount else total_price  # Apply discount
        print("total and final :", total_price, final_price)
        return total_price, final_price

    def save(self, *args, **kwargs):
        """Save instance and update total_price and final_price."""
        super().save(*args, **kwargs)  # Save the instance

    def __str__(self):
        if self.is_shop_the_look:
            return f"Shop The Look: {self.title}"
        return f"Combo Offer: {self.title} - {self.final_price}"

    @property
    def computed_total_price(self):
        """Compute total price dynamically without storing."""
        return sum(product.price for product in self.products.all())

    @property
    def computed_final_price(self):
        """Compute final price dynamically without storing."""
        return self.computed_total_price - (self.discount or 0)

# **Signal to update prices after ManyToManyField changes**
@receiver(m2m_changed, sender=ComboOffer.products.through)
def update_combooffer_prices(sender, instance, action, **kwargs):
    if action in ["post_add", "post_remove", "post_clear"]:  # After changes
        instance.total_price, instance.final_price = instance.calculate_prices()
        instance.save(update_fields=['total_price', 'final_price'])    