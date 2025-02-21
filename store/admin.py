from django.contrib import admin

# Register your models here.
from .models import Store

class StoreAdmin(admin.ModelAdmin):
    list_display = ('id', 'location', 'address', 'contact', 'time_period', 'address_link')

admin.site.register(Store, StoreAdmin)