from rest_framework import serializers
from .models import Order, OrderItem

class OrderSerializer(serializers.ModelSerializer):
    payment_method = serializers.CharField(source="payment_method.name", read_only=True)  # ✅ Return name instead of ID

    class Meta:
        model = Order
        fields = ['order_id', 'customer_name', 'total_price', 'total_discount', 'grand_total', 'email',
                  'mobile', 'tracking_id', 'delivery_option', 'payment_method', 'status', 'razorpay_order_id']
        
        
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