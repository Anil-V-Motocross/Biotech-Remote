from django.db import models
from attribute.models import Size, PlanterSize, Planter, Color, Weight, HandleMaterial, BladeMaterial, PotType, Material, Shape, Litre
from account.models import User

# Create your models here.


class MainProduct(models.Model):
    name = models.CharField(max_length=100, unique=True)

    type_choices = [
        ('plant', 'plant'),
        ('seed', 'seed'),
        ('pot', 'Pot'),
        ('tool', 'Garden Tool'),
    ]
    type = models.CharField(max_length=10, choices=type_choices, default='plant')
    default_sale_price = models.FloatField(default=0)
    default_price = models.FloatField(default=0)
    default_discount = models.FloatField(default=0)
    default_sku = models.FloatField(default=0)

    short_description = models.TextField()
    ribbon = models.CharField(max_length=100)
    threshold = models.CharField(max_length=100)
    description = models.TextField()
    whats_included = models.TextField()
    vedio_link = models.CharField(max_length=200)

    # Flag
    is_featured = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    is_seasonal_collection = models.BooleanField(default=False)
    is_trending = models.BooleanField(default=False)

    # Add-ons: A product can have multiple add-ons (other MainProducts)
    add_ons = models.ManyToManyField('self', symmetrical=False, blank=True)

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
    size_id = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True)
    planter_size_id = models.ForeignKey(PlanterSize, on_delete=models.CASCADE, null=True, blank=True)
    planter_id = models.ForeignKey(Planter, on_delete=models.CASCADE, null=True, blank=True)
    color_id = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)
    weight_id = models.ForeignKey(Weight, on_delete=models.CASCADE, null=True, blank=True)

    # Tool-specific fields
    handle_material_id = models.ForeignKey(HandleMaterial, on_delete=models.SET_NULL, null=True, blank=True)
    blade_material_id = models.ForeignKey(BladeMaterial, on_delete=models.SET_NULL, null=True, blank=True)

    # Pot-specific fields
    material_id = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True)
    shape_id = models.ForeignKey(Shape, on_delete=models.SET_NULL, null=True, blank=True)
    pot_type_id = models.ForeignKey(PotType, on_delete=models.SET_NULL, null=True, blank=True)
    litre_id = models.ForeignKey(Litre, on_delete=models.SET_NULL, null=True, blank=True)

    name = models.CharField(max_length=100)
    cost = models.FloatField(default=0)
    sale_price = models.FloatField(default=0)
    price = models.FloatField(default=0)
    profit = models.FloatField(default=0)
    discount = models.FloatField(default=0)
    stock = models.IntegerField(default=0)
    sku = models.CharField(max_length=40)
    image = models.ImageField(upload_to='product_images/', default='default/category_default.jpg')
    visible_online = models.BooleanField(default=True)
    date_added = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    is_default = models.BooleanField(default=False)


    def __str__(self):
        return self.name
    

class Rating(models.Model):
    main_product_id = models.ForeignKey(MainProduct, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    product_rating = models.DecimalField(max_digits=3, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.product_rating} by {self.user_id} for {self.main_product_id}"

class Review(models.Model):
    main_product_id = models.ForeignKey(MainProduct, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    product_review = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user_id} for {self.main_product_id}"
