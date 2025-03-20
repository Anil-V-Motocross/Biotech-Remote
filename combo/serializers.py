from rest_framework import serializers
from .models import ComboOffer, Product  

# class ComboOfferSerializer(serializers.ModelSerializer):
#     products = serializers.SerializerMethodField()
#     class Meta:
#         model = ComboOffer
#         fields = [
#             'id',
#             'title',
#             'description', 
#             'total_price',
#             'discount',
#             'final_price',
#             'products',
#             'image'
#         ]

#     def get_products(self, obj):
#         """Retrieve names of products included in the combo offer."""
#         return list(obj.products.values_list('name', flat=True))

class ShopTheLookSerializer(serializers.ModelSerializer):
    """Serializer for individual product details"""
    id = serializers.IntegerField(source='product_id.id', read_only=True)

    size = serializers.CharField(source='size_id.name', allow_null=True)
    planter_size = serializers.CharField(source='planter_size_id.name', allow_null=True)
    planter = serializers.CharField(source='planter_id.name', allow_null=True)
    color = serializers.CharField(source='color_id.color_name', allow_null=True)
    weight = serializers.CharField(source='weight_id.size_grams', allow_null=True)
    litre = serializers.CharField(source='litre_id.name', allow_null=True)

    mrp = serializers.FloatField(source='sale_price')

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'mrp', 'price', 'discount',
            'image', 'size', 'planter_size', 'planter',
            'color', 'weight', 'litre'
        ]


class ComboOfferSerializer(serializers.ModelSerializer):
    products = serializers.SerializerMethodField()

    class Meta:
        model = ComboOffer
        fields = [
            'id', 'title', 'description', 'total_price', 'discount',
            'final_price', 'products', 'image'
        ]

    def get_products(self, obj):
        """Return detailed product info for 'shop_the_look' offers, else just names."""
        if obj.is_shop_the_look:
            return ShopTheLookSerializer(obj.products.all(), many=True).data  # Full product details
        return list(obj.products.values_list('name', flat=True))  # Only product names



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

    def validate(self, data):
        """Ensure correct product count based on type."""
        request = self.context.get('request', None)
        products = data.get('products', [])
        is_shop_the_look = data.get('is_shop_the_look', False)

        if request and request.method == 'POST':
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
