from django.contrib import admin
from .models import MainProduct, MainProductImage, ProductCategory, ProductSubCategory, ProductTag
from django.utils.html import format_html

class MainProductAdmin(admin.ModelAdmin):  # Use ModelAdmin for the main admin class
    list_display = ('name', 'short_description', 'ribbon', 'threshold', 'vedio_link')

class MainProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_tag')  # Add a custom method for the image display

    def image_tag(self, obj):
        if obj.image:  # Check if the object has an image
            return format_html('<img src="{}" style="height: 100px; width: auto;" />', obj.image.url)
        return "No Image"

    image_tag.short_description = 'Image'  # Set the column name in the admin panel


class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'category_id')

class ProductSubCategoryAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'subcategory_id')

class ProductTagAdmin(admin.ModelAdmin):
    list_display = ('product_id', 'tag')

admin.site.register(MainProduct, MainProductAdmin)
admin.site.register(MainProductImage, MainProductImageAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(ProductSubCategory, ProductSubCategoryAdmin)
admin.site.register(ProductTag, ProductTagAdmin)
