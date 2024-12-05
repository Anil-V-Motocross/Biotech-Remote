from django.db import models

class Servicelist(models.Model):
    Image=models.ImageField()
    Visible=models.BooleanField(default=False)
    Heading=models.TextField()


class Service_enquiry(models.Model):
    name=models.TextField()
    contact_no=models.IntegerField()
    services=models.TextField()
    location=models.TextField()
    message=models.TextField()
    comment=models.TextField()
    status=models.BooleanField()
    
