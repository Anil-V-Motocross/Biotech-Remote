from rest_framework import serializers
from .models import ComboOffer, Product  

class ComboOfferSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Product.objects.all()
    )  

    class Meta:
        model = ComboOffer
        fields = [
            'id',
            'title',
            'description',
            'image',
            # 'products', 
            'total_price',
            'discount',
            'final_price',
            'is_active',
            # 'date_created',
        ]
