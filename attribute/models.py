from django.db import models

# Create your models here.

class Color(models.Model):
    color_name = models.CharField(max_length=30, blank=False, null=False)
    color_code = models.CharField(max_length=30, blank=False, null=False)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.color_name
    

class Size(models.Model):
    size = models.CharField(max_length=30, blank=False, null=False)
    name = models.CharField(max_length=30, blank=False, null=False)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.size