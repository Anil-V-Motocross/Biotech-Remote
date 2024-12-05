from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from .models import User
from django.contrib.auth.admin import UserAdmin

# Custom UserAdmin class to display relevant fields in the Django admin interface
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'phone_number', 'user_type', 'is_active', 'is_staff', 'date_of_birth', 'created', 'updated')
    list_filter = ('is_active', 'is_staff', 'user_type')
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('email',)

    fieldsets = (
        (None, {
            'fields': ('email', 'password', 'is_superuser')
        }),
        ('Personal info', {
            'fields': ('first_name', 'last_name', 'date_of_birth', 'profile_picture')
        }),
        ('Contact info', {
            'fields': ('phone_number', 'address', 'state', 'city', 'pincode')
        }),
        ('Permissions', {
            'fields': ('groups', )  # Add groups and permissions here
        }),
        ('User Status', {
            'fields': ('otp', 'is_active', 'is_staff', 'user_type')
        }),
        ('Important dates', {
            'fields': ('last_login', 'created', 'updated')
        }),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'user_type', 'is_active', 'is_staff')
        }),
    )

    # Specify which fields should be read-only
    readonly_fields = ('created', 'updated', 'last_login')

# Register the custom User model with the custom UserAdmin
admin.site.register(User, CustomUserAdmin)

# Unregister Group and Permission models if they're already registered
# try:
#     admin.site.unregister(Group)
# except admin.sites.NotRegistered:
#     pass

# try:
#     admin.site.unregister(Permission)
# except admin.sites.NotRegistered:
#     pass
