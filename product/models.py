from django.db import models

# Create your models here.


class MainProduct(models.Model):
    name = models.CharField(max_length=100, unique=True)
    short_description = models.TextField()
    ribbon = models.CharField(max_length=100)
    threshold = models.CharField(max_length=100)
    description = models.TextField()
    whats_included = models.TextField()
    vedio_link = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
class MainProductImage(models.Model):
    product = models.ForeignKey(MainProduct, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"