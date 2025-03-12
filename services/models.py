from django.db import models

class Servicelist(models.Model):
    Heading=models.TextField()
    title=models.CharField(max_length=100, default='default_title')
    Image=models.ImageField()
    Visible=models.BooleanField(default=False)
   
    
    def __str__(self):
        return self.title


class Service_enquiry(models.Model):
    name = models.TextField()
    contact_no = models.IntegerField()
    services = models.TextField()
    location = models.TextField()
    message = models.TextField(blank=True, null=True)
    comment = models.TextField(blank=True, null=True)
    status = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.contact_no}"
    
