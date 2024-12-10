from django.db import models

# Create your models here.
class Banner(models.Model):
    mobile_banner = models.ImageField(upload_to='banners/mobileBanner/')
    web_banner = models.ImageField(upload_to='banners/webBanner/')
    type = models.CharField(max_length=255)
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return self.type