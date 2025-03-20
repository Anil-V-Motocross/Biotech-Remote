from django.db import models
from product.models import MainProduct


class DealOfTheWeek(models.Model):
    main_products = models.OneToOneField(MainProduct, related_name="deals", on_delete=models.CASCADE)
    discount_percentage = models.FloatField(default=0, help_text="Discount percentage for the deal.")
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f"Deal of the Week ({self.start_date.strftime('%Y-%m-%d')} - {self.end_date.strftime('%Y-%m-%d')})"

    class Meta:
        ordering = ['-start_date']  

