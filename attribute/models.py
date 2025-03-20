from django.db import models

# Create your models here.

class Color(models.Model):
    color_name = models.CharField(max_length=30, blank=False, null=False, unique=True)
    color_code = models.CharField(max_length=30, blank=False, null=False, unique=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.color_name
    

class Size(models.Model):
    size = models.CharField(max_length=30, blank=False, null=False, unique=True)
    name = models.CharField(max_length=30, blank=False, null=False, unique=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.size

    
class PlanterSize(models.Model):
    size = models.CharField(max_length=50, blank=False, null=False, unique=True)
    name = models.CharField(max_length=50, blank=False, null=False, unique=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.size
    

class Planter(models.Model):
    name = models.CharField(max_length=50, blank=False, null=False)
    planter_size = models.ForeignKey(PlanterSize, on_delete=models.CASCADE)
    status = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('name', 'planter_size')

    def __str__(self):
        return self.name
    

class Weight(models.Model):
    size_grams = models.CharField(max_length=50)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.size_grams

class Litre(models.Model):
    name = models.CharField(max_length=50, unique=True)
    status = models.BooleanField(default=True) 

    def __str__(self):
        return self.name    

class Material(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., "Ceramic", "Plastic", "Metal"
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Shape(models.Model):
    name = models.CharField(max_length=50, unique=True)  # e.g., "Round", "Rectangle"
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class PotType(models.Model):
    name = models.CharField(max_length=50, unique=True) # Wall, Rope, Hanging
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class HandleMaterial(models.Model):
    name = models.CharField(max_length=50, unique=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class BladeMaterial(models.Model):
    name = models.CharField(max_length=50, unique=True)
    status = models.BooleanField(default=True)

    def __str__(self):
        return self.name    

