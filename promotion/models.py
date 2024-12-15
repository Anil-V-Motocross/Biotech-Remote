from django.db import models

# Create your models here.
class Banner(models.Model):
    mobile_banner = models.ImageField(upload_to='banners/mobileBanner/')
    web_banner = models.ImageField(upload_to='banners/webBanner/')
    type = models.CharField(max_length=255)
    is_visible = models.BooleanField(default=True)

    def __str__(self):
        return self.type


class ContactUs(models.Model):
    name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    message = models.TextField()
    comment = models.TextField(null=True, blank=True)
    status = models.CharField(max_length=100, default='Pending')

    def __str__(self):
        return self.name