from django.db import models
from product.models import Product

class ComboOffer(models.Model):
    title = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='combo_images/', default='default/combo_default.jpg')
    products = models.ManyToManyField(Product, related_name='combo_offers')

    # These fields are automatically calculated (no user input)
    total_price = models.FloatField(null=True, blank=True)  # Allow NULL values
    discount = models.FloatField(default=0)  # User provides discount
    final_price = models.FloatField(null=True, blank=True)  # Allow NULL values

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
        # Calculate prices before saving
        if self.pk:  # Check if the instance already exists
            total_price, final_price = self.calculate_prices()
            self.total_price = total_price
            self.final_price = final_price
            print("self.pk", total_price,final_price)
        super().save(*args, **kwargs)  # Save the instance

        # If the instance is being created (not updated), we need to save again to update the prices
        if not self.pk:
            total_price, final_price = self.calculate_prices()
            self.total_price = total_price
            self.final_price = final_price
            print("not self.pk ---:", total_price, final_price)
            super().save(update_fields=['total_price', 'final_price'])  # Save updated values

    def __str__(self):
        return f"{self.title} - {self.final_price}"

    @property
    def computed_total_price(self):
        """Compute total price dynamically without storing."""
        return sum(product.price for product in self.products.all())

    @property
    def computed_final_price(self):
        """Compute final price dynamically without storing."""
        return self.computed_total_price - (self.discount or 0)