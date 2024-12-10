from django.contrib import admin
from .models import Color, Size, Planter, PlanterSize

# Register your models here.

class ColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'color_name', 'color_code', 'status')

class SizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'size', 'status')

class PlanterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status')

class PlanterSizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'size', 'status')


admin.site.register(Planter, PlanterAdmin)
admin.site.register(Color, ColorAdmin)
admin.site.register(Size, SizeAdmin)