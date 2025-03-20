from django.contrib import admin
from dealoftheweek.models import DealOfTheWeek

@admin.register(DealOfTheWeek)
class DealOfTheWeekAdmin(admin.ModelAdmin):
    list_display = ('id', 'start_date', 'end_date', 'is_active', 'discount_percentage')

    

