from django.contrib import admin
from services.models import *

# Register your models here.

class ServicelistAdmin(admin.ModelAdmin):
    list_display = ('Heading', 'title', 'Image', 'Visible')


class ServiceEnquiryAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_no', 'services', 'location', 'message', 'comment', 'status')

admin.site.register(Servicelist, ServicelistAdmin)
admin.site.register(Service_enquiry, ServiceEnquiryAdmin)
