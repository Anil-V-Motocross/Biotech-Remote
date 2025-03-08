from django.contrib import admin
from .models import ComboOffer

@admin.register(ComboOffer)
class ComboOfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'final_price', 'discount', 'is_active', 'date_created')
    filter_horizontal = ('products',)
    search_fields = ('title',)
