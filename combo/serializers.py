from rest_framework import serializers
from .models import ComboOffer, Product  

class ComboOfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComboOffer
        fields = [
            'id',
            'title',
            'description', 
            'total_price',
            'discount',
            'final_price',
        ]

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name']

class AdminComboOfferSerializer(serializers.ModelSerializer):
    products = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all(),  # Accept product IDs in write mode
        many=True,
        write_only=True
    )
    product_details = ProductSerializer(source='products', many=True, read_only=True)

    class Meta:
        model = ComboOffer
        fields = '__all__'        