from rest_framework import serializers
from .models import Coupon
from category.models import Category
from product.models import MainProduct


class CouponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Coupon
        fields = [
            'id',
            'code',
            'discount_type',
            'discount_value',
            'max_discount_value',
            'description',
            'start_date',
            'end_date',
            'minimum_order_value',
            'is_stackable',
            'redemption_message',
        ]


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']  # Include any other fields if needed

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainProduct
        fields = ['id', 'name']  

class CouponAdminSerializer(serializers.ModelSerializer):
    applicable_categories = CategorySerializer(many=True, read_only=True)  # Returns full category details
    applicable_products = ProductSerializer(many=True, read_only=True)  # Returns full product details
    
    # Accepts IDs for create/update
    applicable_category_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Category.objects.all(), 
        write_only=True, 
        source="applicable_categories",
        required=False
    )
    applicable_product_ids = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=MainProduct.objects.all(), 
        write_only=True, source="applicable_products",
        required=False
    )
    class Meta:
        model = Coupon
        fields = '__all__'
        read_only_fields = ('used_count',) 

    # def validate(self, data):
    #     # Ensure a coupon applies to either categories or products, but not both
    #     applicable_categories = data.get('applicable_categories', [])
    #     applicable_products = data.get('applicable_products', [])

    #     if applicable_categories and applicable_products:
    #         raise serializers.ValidationError("A coupon can be applied to either categories OR products, not both.")

    #     # if not applicable_categories and not applicable_products:
    #     #     raise serializers.ValidationError("A coupon must be applied to either categories or products.")

        #     return data
    def validate(self, data):
        request = self.context.get('request') 
        request_method = request.method if request else 'POST'

        # Only enforce validation during creation
        if request_method == 'POST':
            # Fetch existing data from the instance if available
            applicable_categories = data.get('applicable_categories', self.instance.applicable_categories.all() if self.instance else [])
            applicable_products = data.get('applicable_products', self.instance.applicable_products.all() if self.instance else [])
            is_first_order = data.get('is_first_order', self.instance.is_first_order if self.instance else False)

            selected_fields = sum(bool(x) for x in [applicable_categories, applicable_products, is_first_order])
            if selected_fields != 1:  # Exactly one should be true
                raise serializers.ValidationError("A coupon must apply to either categories, products, or be a first-order coupon, but not multiple.")

        return data

