from django.db import models

# Create your models here.

class Color(models.Model):
    color_name = models.CharField(max_length=30)
    color_code = models.CharField(max_length=30)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.color_name