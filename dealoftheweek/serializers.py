from rest_framework import serializers
from .models import DealOfTheWeek
from product.models import MainProduct


class DealOfTheWeekSerializer(serializers.ModelSerializer):
    main_products = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # Only return product IDs

    class Meta:
        model = DealOfTheWeek
        fields = ['main_products']

# class AdminDealOfTheWeekSerializer(serializers.ModelSerializer):
#     main_products = serializers.SerializerMethodField()  # Override `main_products`

#     class Meta:
#         model = DealOfTheWeek
#         fields = '__all__'  

#     def get_main_products(self, obj):
#         return obj.main_products.name if obj.main_products else None

class AdminDealOfTheWeekSerializer(serializers.ModelSerializer):
    main_products = serializers.PrimaryKeyRelatedField(queryset=MainProduct.objects.all())

    class Meta:
        model = DealOfTheWeek
        fields = '__all__'

    def to_representation(self, instance):
        """ Convert the main_products field to product name in GET response. """
        data = super().to_representation(instance)
        data['main_products'] = instance.main_products.name if instance.main_products else None
        return data