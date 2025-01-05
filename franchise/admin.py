from django.contrib import admin
from .models import Franchise

# Register your models here.

class FranchiseAdmin(admin.ModelAdmin):
    list_display = ('name', 'mobile', 'email', 'area', 'address', 'message')

admin.site.register(Franchise, FranchiseAdmin)