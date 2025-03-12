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
            'image'
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

    # def validate_products(self, value):
    #     """Ensure at least two products are selected."""
    #     if len(value) < 2:
    #         raise serializers.ValidationError("A combo offer must contain at least two products.")
    #     return value 

    def validate(self, data):
        """Ensure correct product count based on type."""
        products = data.get('products', [])
        is_shop_the_look = data.get('is_shop_the_look', False)

        if not is_shop_the_look and len(products) < 2:
            raise serializers.ValidationError({"products": "A combo offer must contain at least two products."})

        return data

    def create(self, validated_data):
        """Create ComboOffer and auto-calculate prices."""
        products = validated_data.pop('products', [])
        combo = ComboOffer.objects.create(**validated_data)
        combo.products.set(products)  # Add products to ManyToMany field
        combo.save()  # Triggers price calculations
        return combo

    def update(self, instance, validated_data):
        """Update ComboOffer and recalculate prices if needed."""
        products = validated_data.pop('products', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if products is not None:
            instance.products.set(products)

        instance.save()
        return instance
