from django.contrib import admin
from .models import Color, Size

# Register your models here.

class ColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'color_name', 'color_code', 'status')

class SizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'size', 'status')

admin.site.register(Color, ColorAdmin)
admin.site.register(Size, SizeAdmin)