from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from .models import User, InitialInfo, Address
from django.contrib.auth.admin import UserAdmin

# Custom UserAdmin class to display relevant fields in the Django admin interface
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('id', 'email', 'first_name', 'last_name', 'mobile', 'is_active', 'is_staff', 'date_of_birth', 'created', 'updated')
    list_filter = ('is_active', 'is_staff',)
    search_fields = ('email', 'first_name', 'last_name', 'mobile')
    ordering = ('email',)

    fieldsets = (
        (None, {
            'fields': ('email', 'password', 'is_superuser')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'profile_picture', 'gender')
        }),
        ('Contact info', {
            'fields': ('mobile',)
        }),
        ('Permissions', {
            'fields': ('groups', )  # Add groups and permissions here
        }),
        ('User Status', {
            'fields': ('otp', 'is_active', 'is_staff',)
        }),
        ('Important dates', {
            'fields': ('last_login', 'created', 'updated')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'mobile', 'is_active', 'is_staff')
        }),
    )

    # Specify which fields should be read-only
    readonly_fields = ('created', 'updated', 'last_login')

class InitialInfoAdmin(admin.ModelAdmin):
    list_display = ('id', 'mobile', 'otp', 'name', 'email', 'referal_code')
    
class AddressAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'city', 'state', 'pincode')

# Register the custom User model with the custom UserAdmin
admin.site.register(User, CustomUserAdmin)

# Register the InitialInfo model
admin.site.register(InitialInfo, InitialInfoAdmin)

# Register the Address model
admin.site.register(Address, AddressAdmin)

# Unregister Group and Permission models if they're already registered
# try:
#     admin.site.unregister(Group)
# except admin.sites.NotRegistered:
#     pass

# try:
#     admin.site.unregister(Permission)
# except admin.sites.NotRegistered:
#     pass
