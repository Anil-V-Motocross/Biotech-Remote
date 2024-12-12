from django.contrib import admin

# Register your models here.
from .models import Carrier

class CarrierAdmin(admin.ModelAdmin):
    list_display = ('categories', 'position_name', 'job_summary', 'responsibilities', 'desired_skills')

admin.site.register(Carrier, CarrierAdmin)