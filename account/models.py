from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils.translation import gettext_lazy as _

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
    user_id = models.CharField(max_length=50, null=True, blank=True)
    first_name = models.CharField(max_length=100)  # Changed from firstName
    last_name = models.CharField(max_length=100, null=True, blank=True)  # Changed from lastName
    date_of_birth = models.DateField(null=True, blank=True)  # Changed from dateOfBirth
    profile_picture = models.ImageField(upload_to='profile_image/', default='default/profile_default.png', null=True, blank=True)  # Changed from profilePicture
    gender = models.CharField(max_length=20, null=True, blank=True)
    bmu = models.CharField(max_length=20, default='0')
    
    # Contact Data
    mobile = models.CharField(max_length=20, unique=True, blank=False, null=False)
    email = models.EmailField(_('email address'), unique=True)

    # User Status
    otp = models.CharField(max_length=10, null=True, blank=True)
    is_active = models.BooleanField(default=False, verbose_name='status')
    is_staff = models.BooleanField(default=False)

    referal_code = models.CharField(max_length=15, null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = CustomAccountManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['mobile']

    class Meta:
        verbose_name_plural = "Account"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    

class InitialInfo(models.Model):
    mobile = models.CharField(max_length=15, null=True, blank=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    referal_code = models.CharField(max_length=15, null=True, blank=True)
    
    
class Address(models.Model):
   
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    address = models.TextField(max_length=200)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    pincode = models.IntegerField()
    is_default = models.BooleanField(default=False)
    address_types=[
        ('Home', 'Home'),
        ('Work', 'Work'),
    ]
    address_type = models.CharField(max_length=255,choices=address_types)
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name="user_address")

    def __str__(self):
        return f"{self.user}, {self.city}, {self.state}, {self.pincode}"

