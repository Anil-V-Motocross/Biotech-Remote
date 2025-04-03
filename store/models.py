from django.db import models

# Create your models here.
class Store(models.Model):
    location = models.CharField(max_length=255)
    address = models.TextField()
    contact = models.CharField(max_length=255)
    time_period = models.CharField(max_length=50)
    address_link = models.URLField()
    image = models.ImageField(upload_to='store_images/', null=True, blank=True)

    def __str__(self):
        return self.location