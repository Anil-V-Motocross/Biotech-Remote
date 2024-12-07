from django.contrib import admin
from .models import Color

# Register your models here.

class ColorAdmin(admin.ModelAdmin):
    list_display = ('color_name', 'color_code', 'status')

admin.site.register(Color, ColorAdmin)