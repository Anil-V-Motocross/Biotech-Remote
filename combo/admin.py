from django.contrib import admin
from .models import ComboOffer

@admin.register(ComboOffer)
class ComboOfferAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'total_price', 'discount', 'final_price', 'is_shop_the_look', 'is_active', 'date_created')
    filter_horizontal = ('products',)
    search_fields = ('title',)
