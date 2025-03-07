from rest_framework import serializers
from .models import Order

class OrderSerializer(serializers.ModelSerializer):
    payment_method = serializers.CharField(source="payment_method.name", read_only=True)  # ✅ Return name instead of ID

    class Meta:
        model = Order
        fields = ['order_id', 'customer_name', 'total_price', 'total_discount', 'grand_total', 'email',
                  'mobile', 'tracking_id', 'delivery_option', 'payment_method', 'status', 'razorpay_order_id']