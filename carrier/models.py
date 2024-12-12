from django.db import models

# Create your models here.
class Carrier(models.Model):
    categories = models.CharField(max_length=100)
    position_name = models.CharField(max_length=100)
    job_summary = models.TextField()
    responsibilities = models.TextField()
    desired_skills = models.TextField()

    def __str__(self):
        return self.position_name