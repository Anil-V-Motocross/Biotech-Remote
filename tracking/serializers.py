from rest_framework import serializers
from .models import DeliveryLocation

class PincodeCheckSerializer(serializers.Serializer):
    pincode = serializers.CharField(max_length=6)

class BulkPincodeSerializer(serializers.Serializer):
    pincodes = serializers.ListField(
        child=serializers.CharField(max_length=6),
        allow_empty=False
    )

class DeliveryLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryLocation
        fields = ['pincode', 'city', 'state', 'created_at']