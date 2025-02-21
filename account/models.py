from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from datetime import datetime


class CustomAccountManager(BaseUserManager):
    def create_superuser(self, email, password, **other_fields):
        other_fields.setdefault('is_staff', True)
        other_fields.setdefault('is_superuser', True)
        other_fields.setdefault('is_active', True)
        return self.create_user(email, password=password, **other_fields)

    def create_user(self, email, password, **other_fields):
        if not email:
            raise ValueError(_('You must provide an email address'))
        email = self.normalize_email(email)
        user = self.model(email=email, **other_fields)
        user.set_password(password)
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.CharField(max_length=255, null=True, blank=True)
    first_name = models.CharField(max_length=255)  # Changed from firstName
    last_name = models.CharField(max_length=255, null=True, blank=True)  # Changed from lastName
    date_of_birth = models.DateField(null=True, blank=True)  # Changed from dateOfBirth
    profile_picture = models.ImageField(upload_to='profile_image/', default='default/profile_default.png', null=True, blank=True)  # Changed from profilePicture

    # Contact Data
    phone_number = models.CharField(max_length=20, unique=True, blank=False, null=False)
    email = models.EmailField(_('email address'), unique=True)

    # Address Data
    address = models.TextField(max_length=500, blank=True)  # Changed from Address
    state = models.CharField(max_length=255, null=True, blank=True)
    city = models.CharField(max_length=255, null=True, blank=True)
    pincode = models.CharField(max_length=255, null=True, blank=True)

    # User Status
    otp = models.CharField(max_length=10, null=True, blank=True)
    is_active = models.BooleanField(default=False, verbose_name='status')
    is_staff = models.BooleanField(default=False)

    # User Type
    user_type_choices = [
        ('customer', 'Customer'),
        ('vendor', 'Vendor'),
        ('sub_admin', 'Sub Admin'),  # Changed from 'sub admin' to 'sub_admin' for snake_case
        ('sales', 'Sales'),
    ]
    user_type = models.CharField(max_length=20, choices=user_type_choices, default='customer')

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['phone_number']

    class Meta:
        verbose_name_plural = "Account"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class InitialInfo(models.Model):
    mobile = models.CharField(max_length=15, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    referell_code = models.CharField(max_length=15, null=True, blank=True)

    def __str__(self):
        return f"{self.mobile}"