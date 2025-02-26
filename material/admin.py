from django.contrib import admin
from .models import (
    Material, Shape, PotType, HandleMaterial, BladeMaterial,
    InventoryItem, InventoryItemImage, PotVariant, PotVariantImage,
    ToolVariant, ToolVariantImage, Rating, Review
)

# Inline admin classes for images
class InventoryItemImageInline(admin.TabularInline):
    model = InventoryItemImage
    extra = 1  # Allows adding multiple images at once

class PotVariantImageInline(admin.TabularInline):
    model = PotVariantImage
    extra = 1

class ToolVariantImageInline(admin.TabularInline):
    model = ToolVariantImage
    extra = 1

# Admin for Inventory Items
@admin.register(InventoryItem)
class InventoryItemAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'mrp', 'sale_price', 'average_rating', 'material', 'date_added')
    list_filter = ('category', 'is_featured', 'is_best_seller', 'is_seasonal_collection', 'is_trending')
    search_fields = ('name', 'category')
    inlines = [InventoryItemImageInline]

# Admin for Pot Variants
@admin.register(PotVariant)
class PotVariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'inventory_item', 'size', 'color', 'pot_type', 'litre', 'mrp', 'sale_price', 'stock', 'visible_online')
    list_filter = ('size', 'color', 'pot_type', 'visible_online')
    search_fields = ('inventory_item__name', 'pot_type__name')
    inlines = [PotVariantImageInline]

# Admin for Tool Variants
@admin.register(ToolVariant)
class ToolVariantAdmin(admin.ModelAdmin):
    list_display = ('id', 'inventory_item', 'size', 'color', 'handle_material', 'blade_material', 'mrp', 'sale_price', 'stock', 'visible_online')
    list_filter = ('size', 'color', 'handle_material', 'blade_material', 'visible_online')
    search_fields = ('inventory_item__name',)
    inlines = [ToolVariantImageInline]

# Admin for Ratings
@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'inventory_item', 'user', 'product_rating', 'date')
    list_filter = ('product_rating', 'date')
    search_fields = ('inventory_item__name', 'user__email')

# Admin for Reviews
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'inventory_item', 'user', 'date')
    search_fields = ('inventory_item__name', 'user__email')

@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(Shape)
class ShapeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(PotType)
class PotTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(HandleMaterial)
class HandleMaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')

@admin.register(BladeMaterial)
class BladeMaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')


