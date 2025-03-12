# serializers.py
from rest_framework import serializers

from .models import Service_enquiry, Servicelist  # This is okay
# Avoid importing views or other modules that import views here.


class ServiceEnquirySerializer(serializers.ModelSerializer):
    message = serializers.CharField(required=False, allow_blank=True)
    comment = serializers.CharField(required=False, allow_blank=True)
    status = serializers.BooleanField(required=False)

    class Meta:
        model = Service_enquiry
        fields = '__all__'



class ServiceListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Servicelist
        fields = '__all__'  # Or specify fields like ['name', 'contact_no', ...]
