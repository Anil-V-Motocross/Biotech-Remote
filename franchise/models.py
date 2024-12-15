from django.db import models

# Create your models here.

class Franchise(models.Model):  
    name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    area = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    message = models.TextField()

    def __str__(self):
        return self.name