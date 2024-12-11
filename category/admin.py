from django.contrib import admin
from .models import Category, SubCategory
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'is_published')


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'category', 'is_published')
    
admin.site.register(Category)
admin.site.register(SubCategory, SubCategoryAdmin)
