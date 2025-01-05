from django.db import models
from attribute.models import Size, PlanterSize, Planter, Color, Weight

# Create your models here.


class MainProduct(models.Model):
    name = models.CharField(max_length=100, unique=True)

    type_choices = [
        ('plant', 'plant'),
        ('seed', 'seed'),
    ]
    type = models.CharField(max_length=10, choices=type_choices, default='plant')

    short_description = models.TextField()
    ribbon = models.CharField(max_length=100)
    threshold = models.CharField(max_length=100)
    description = models.TextField()
    whats_included = models.TextField()
    vedio_link = models.CharField(max_length=200)

    is_featured = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_seasonal_collection = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class MainProductImage(models.Model):
    product = models.ForeignKey(MainProduct, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='main_product_images/')

    def __str__(self):
        return f"Image for {self.product.name}"
    
class ProductCategory(models.Model):
    product_id = models.ForeignKey(MainProduct, on_delete=models.CASCADE)
    category_id = models.ForeignKey('category.Category', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product_id.name} - {self.category_id.name}"
    

class ProductSubCategory(models.Model):
    product_id = models.ForeignKey(MainProduct, on_delete=models.CASCADE)
    subcategory_id = models.ForeignKey('category.SubCategory', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.product_id.name} - {self.subcategory_id.name}"
    

class ProductTag(models.Model):
    product_id = models.ForeignKey(MainProduct, on_delete=models.CASCADE)
    tag = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.product_id.name} - {self.tag}"
    

class Product(models.Model):
    product_id = models.ForeignKey(MainProduct, on_delete=models.CASCADE)
    size_id = models.ForeignKey(Size, on_delete=models.CASCADE, null=True)
    planter_size_id = models.ForeignKey(PlanterSize, on_delete=models.CASCADE, null=True)
    planter_id = models.ForeignKey(Planter, on_delete=models.CASCADE, null=True)
    color_id = models.ForeignKey(Color, on_delete=models.CASCADE, null=True)
    weight_id = models.ForeignKey(Weight, on_delete=models.CASCADE, null=True)

    name = models.CharField(max_length=100)
    cost = models.CharField(max_length=10)
    sale_price = models.CharField(max_length=10)
    price = models.CharField(max_length=10)
    profit = models.CharField(max_length=10)
    discount = models.CharField(max_length=10)
    stock = models.CharField(max_length=10)
    sku = models.CharField(max_length=40)
    image = models.ImageField(upload_to='product_images/', default='default/category_default.jpg')
    visible_online = models.BooleanField(default=True)

    is_default = models.BooleanField(default=False)


    def __str__(self):
        return self.name
    