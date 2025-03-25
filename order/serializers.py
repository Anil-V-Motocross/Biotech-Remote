from rest_framework import serializers
from rest_framework import serializers
from order.models import Order, OrderItem, DeliveryAddress
from account.models import Address


class OrderSerializer(serializers.ModelSerializer):
    payment_method = serializers.CharField(source="payment_method.name", read_only=True)  # ✅ Return name instead of ID

    class Meta:
        model = Order
        fields = ['id', 'order_id', 'customer_name', 'total_price', 'total_discount', 'grand_total', 'email',
                  'mobile', 'tracking_id', 'delivery_option', 'payment_method', 'razorpay_order_id', 'coupon_discount']
        
        
class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = '__all__'
        
    # add main product name from to_representation
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['product_name'] = instance.product_id.product_id.name
        return representation

class PlaceOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'        





class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = '__all__'

# class OrderItemSerializer(serializers.ModelSerializer):
#     product_name = serializers.SerializerMethodField()

#     class Meta:
#         model = OrderItem
#         fields = [
#             'id', 'sku', 'image', 'quantity', 'price', 'sale_price', 'discount', 'total', 
#             'hsn_code', 'order_id', 'product_id', 'combo_offer', 'product_name'
#         ]

#     def get_product_name(self, obj):
#         return obj.product_id.product_id.name

# class OrderSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Order
#         fields = [
#             'id', 'order_id', 'date', 'customer_name', 'email', 'mobile', 'total_price', 
#             'total_discount', 'grand_total', 'tracking_id', 'delivery_option', 'payment_method', 
#             'status', 'razorpay_order_id', 'is_combo_purchase', 'coupon_applied', 
#             'coupon_discount', 'customer_id', 'applied_coupon'
#         ]

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = [
            'id', 'first_name', 'last_name', 'address', 'state', 'city', 'pincode', 
            'is_default', 'address_type', 'user'
        ]        