from django.contrib import admin
from .models import Banner, ContactUs

# Register your models here.
class BannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'mobile_banner', 'web_banner', 'type', 'is_visible')


class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'mobile', 'email')

admin.site.register(Banner, BannerAdmin)
admin.site.register(ContactUs, ContactUsAdmin)