from django.db import models

# Create your models here.

class FranchiseEnquiry(models.Model):  
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
    ]


    name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    area = models.CharField(max_length=200)
    address = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return self.name