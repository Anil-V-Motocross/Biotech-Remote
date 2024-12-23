from django.contrib import admin
from .models import Color, Size, Planter, PlanterSize, Weight

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


admin.site.register(PlanterSize, PlanterSizeAdmin)
admin.site.register(Planter, PlanterAdmin)
admin.site.register(Color, ColorAdmin)
admin.site.register(Size, SizeAdmin)
admin.site.register(Weight, WeightAdmin)