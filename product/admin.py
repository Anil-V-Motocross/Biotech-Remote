from django.contrib import admin
from .models import MainProduct, MainProductImage, ProductCategory, ProductSubCategory, ProductTag, Product, Rating, Review, ProductViewCount, RecentlyViewedProduct
from django.utils.html import format_html

class MainProductAdmin(admin.ModelAdmin):  # Use ModelAdmin for the main admin class
    list_display = ('id', 'type', 'name', 'default_price', 'default_sale_price', 'default_discount', 'default_sku', 'ribbon', 'threshold', 'vedio_link')
    filter_horizontal = ('add_ons',)
    
class MainProductImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'image_tag')  # Add a custom method for the image display

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


class ProductAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'product_id', 'sku', 'stock', 'date_added', 'visible_online')
    list_filter = ('product_id', 'size_id', 'planter_size_id', 'planter_id', 'color_id', 'weight_id')

class RatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'main_product_id', 'user_id', 'product_rating', 'date_created')
    
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'main_product_id', 'user_id', 'review_title', 'date_created')


@admin.register(RecentlyViewedProduct)
class RecentlyViewedProductAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'viewed_at')
    search_fields = ('user__username', 'product__name')
    list_filter = ('viewed_at',)
    ordering = ('-viewed_at',)

@admin.register(ProductViewCount)
class ProductViewCountAdmin(admin.ModelAdmin):
    list_display = ('id', 'product', 'count')
    search_fields = ('product__name',)
    ordering = ('-count',)

admin.site.register(MainProduct, MainProductAdmin)
admin.site.register(MainProductImage, MainProductImageAdmin)
admin.site.register(ProductCategory, ProductCategoryAdmin)
admin.site.register(ProductSubCategory, ProductSubCategoryAdmin)
admin.site.register(ProductTag, ProductTagAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(Review, ReviewAdmin)
