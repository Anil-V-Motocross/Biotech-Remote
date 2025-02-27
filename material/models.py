
# from django.db import models
# from django.core.validators import MinValueValidator
# from django.db.models import Avg
# from account.models import User  
# from attribute.models import Color, Size

# class Material(models.Model):
#     name = models.CharField(max_length=50, unique=True)  # e.g., "Ceramic", "Plastic", "Metal"

#     def __str__(self):
#         return self.name

# class Shape(models.Model):
#     name = models.CharField(max_length=50, unique=True)  # e.g., "Round", "Rectangle"

#     def __str__(self):
#         return self.name

# class PotType(models.Model):
#     name = models.CharField(max_length=50, unique=True)

#     def __str__(self):
#         return self.name

# class HandleMaterial(models.Model):
#     name = models.CharField(max_length=50, unique=True)

#     def __str__(self):
#         return self.name

# class BladeMaterial(models.Model):
#     name = models.CharField(max_length=50, unique=True)

#     def __str__(self):
#         return self.name

# # Main Inventory Model
# class InventoryItem(models.Model):  
#     CATEGORY_CHOICES = [
#         ('pot', 'Pot'),
#         ('tool', 'Garden Tool'),
#     ]
    
#     name = models.CharField(max_length=100)  
#     category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
#     material = models.ForeignKey(Material, on_delete=models.SET_NULL, null=True, blank=True)
#     shape = models.ForeignKey(Shape, on_delete=models.SET_NULL, null=True, blank=True) 
#     short_description = models.CharField(max_length=255, null=True, blank=True) 
#     long_description = models.TextField(null=True, blank=True)  
#     mrp = models.FloatField(default=0)  
#     sale_price = models.FloatField(default=0)  
#     discount = models.FloatField(default=0) 
#     whats_in_the_box = models.TextField(null=True, blank=True)  
#     date_added = models.DateTimeField(auto_now_add=True)

#     # Dynamic Fields
#     additional_attributes = models.JSONField(default=dict, blank=True, null=True)  

#     # Average Rating (denormalized for performance)
#     average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, blank=True)

#     # Flags for filtering
#     is_featured = models.BooleanField(default=False)
#     is_best_seller = models.BooleanField(default=False)
#     is_seasonal_collection = models.BooleanField(default=False)
#     is_trending = models.BooleanField(default=False)

#     def update_average_rating(self):
#         """Update the average rating when a new rating is added."""
#         avg_rating = self.ratings.aggregate(avg=Avg('product_rating'))['avg']
#         self.average_rating = avg_rating if avg_rating else 0
#         self.save()

#     def __str__(self):
#         return self.name

# class InventoryItemImage(models.Model):
#     inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="images")
#     image = models.ImageField(upload_to='inventory_images/')

#     def __str__(self):
#         return f"Image for {self.inventory_item.name}"

# # Variant Model for Pots
# class PotVariant(models.Model):   
#     inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="pot_variants")
#     size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
#     color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
#     pot_type = models.ForeignKey(PotType, on_delete=models.SET_NULL, null=True, blank=True)
#     litre = models.FloatField(null=True, blank=True)  

#     # Pricing
#     mrp = models.FloatField(default=0)
#     sale_price = models.FloatField(default=0)
#     discount = models.FloatField(default=0)
#     profit = models.FloatField(default=0)
#     stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])  # Prevents negative stock
#     visible_online = models.BooleanField(default=True)
#     date_added = models.DateTimeField(auto_now_add=True, null=True, blank=True)

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['inventory_item', 'size', 'color', 'pot_type', 'litre'],
#                 name='unique_pot_variant'
#             )
#         ]

#     def __str__(self):
#         return f"{self.inventory_item.name} - {self.size} - {self.color} - {self.pot_type} - {self.litre}L"

# class PotVariantImage(models.Model):
#     pot_variant = models.ForeignKey(PotVariant, on_delete=models.CASCADE, related_name="images")
#     image = models.ImageField(upload_to='pot_variant_images/')

#     def __str__(self):
#         return f"Image for {self.pot_variant}"

# # Variant Model for Tools
# class ToolVariant(models.Model):
#     inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="tool_variants")
#     size = models.ForeignKey(Size, on_delete=models.SET_NULL, null=True, blank=True)
#     color = models.ForeignKey(Color, on_delete=models.SET_NULL, null=True, blank=True)
#     handle_material = models.ForeignKey(HandleMaterial, on_delete=models.SET_NULL, null=True, blank=True)
#     blade_material = models.ForeignKey(BladeMaterial, on_delete=models.SET_NULL, null=True, blank=True)

#     # Pricing
#     mrp = models.FloatField(default=0)
#     sale_price = models.FloatField(default=0)
#     discount = models.FloatField(default=0)
#     profit = models.FloatField(default=0)
#     stock = models.IntegerField(default=0, validators=[MinValueValidator(0)])
#     visible_online = models.BooleanField(default=True)
#     date_added = models.DateTimeField(auto_now_add=True, null=True, blank=True)

#     class Meta:
#         constraints = [
#             models.UniqueConstraint(
#                 fields=['inventory_item', 'size', 'color', 'handle_material', 'blade_material'],
#                 name='unique_tool_variant'
#             )
#         ]

#     def __str__(self):
#         return f"{self.inventory_item.name} - {self.size} - {self.color} - {self.handle_material} - {self.blade_material}"

# class ToolVariantImage(models.Model):
#     tool_variant = models.ForeignKey(ToolVariant, on_delete=models.CASCADE, related_name="images")
#     image = models.ImageField(upload_to='tool_variant_images/')

#     def __str__(self):
#         return f"Image for {self.tool_variant}"

# # Ratings for Inventory Items
# class Rating(models.Model):
#     inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="ratings")
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inventory_ratings")
#     product_rating = models.DecimalField(max_digits=3, decimal_places=2, validators=[MinValueValidator(0)])
#     date = models.DateTimeField(auto_now_add=True)

#     def save(self, *args, **kwargs):
#         """Auto-update average rating on save."""
#         super().save(*args, **kwargs)
#         self.inventory_item.update_average_rating()

#     def __str__(self):
#         return f"Rating {self.product_rating} by {self.user} for {self.inventory_item.name}"

#     class Meta:
#         ordering = ['-date']  # Show newest ratings first

# # Reviews for Inventory Items
# class Review(models.Model):
#     inventory_item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name="reviews")
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inventory_reviews")
#     product_review = models.TextField()
#     date = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f"Review by {self.user} for {self.inventory_item.name}"

#     class Meta:
#         ordering = ['-date'] 
