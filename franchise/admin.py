from django.contrib import admin
from .models import FranchiseEnquiry

# Register your models here.

class FranchiseAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'email', 'area', 'address', 'status')

admin.site.register(FranchiseEnquiry, FranchiseAdmin)