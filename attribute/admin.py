from django.contrib import admin
from .models import Color, Size, Planter, PlanterSize, Weight, Material, Shape, HandleMaterial, BladeMaterial, PotType

# Register your models here.

class ColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'color_name', 'color_code', 'status')

class SizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'size', 'status')

class PlanterSizeAdmin(admin.ModelAdmin):
    list_display = ('id', 'size', 'status')


class PlanterAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'planter_size', 'status')


class WeightAdmin(admin.ModelAdmin):
    list_display = ('id', 'size_grams', 'status')    

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

admin.site.register(PlanterSize, PlanterSizeAdmin)
admin.site.register(Planter, PlanterAdmin)
admin.site.register(Color, ColorAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Weight, WeightAdmin)