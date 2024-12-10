from django.contrib import admin
from .models import Banner

# Register your models here.
class BannerAdmin(admin.ModelAdmin):
    list_display = ('mobile_banner', 'web_banner', 'type', 'is_visible')

admin.site.register(Banner, BannerAdmin)