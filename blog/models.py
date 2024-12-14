from django.db import models

# Create your models here.
class Blog(models.Model):
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='blog_images/')
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return self.title