from rest_framework import serializers
from .models import FranchiseEnquiry

class FranchiseEnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = FranchiseEnquiry
        fields = '__all__' 