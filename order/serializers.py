from rest_framework import serializers
from rest_framework import serializers
from order.models import Order, OrderItem, DeliveryAddress
from account.models import Address



class OrderSerializer(serializers.ModelSerializer):
    payment_method = serializers.CharField(read_only=True) 
    pickup_store = serializers.SerializerMethodField()  
    pickup_deadline = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)  

    class Meta:
        model = Order
        fields = [
            'id', 'order_id', 'customer_name', 'total_price', 'total_discount', 'grand_total', 
            'email', 'mobile', 'tracking_id', 'delivery_option', 'payment_method', 
            'razorpay_order_id', 'coupon_discount', 'pickup_deadline', 'pickup_store'
        ]
    
    def get_pickup_store(self, obj):
        """
        Returns store details if the delivery option is 'Pick Up Store'.
        """
        if obj.delivery_option == "PickUpStore" and obj.store_id:
            return {
                "id": obj.store_id.id,
                "location": obj.store_id.location,
                "address": obj.store_id.address,
                "contact": obj.store_id.contact,
                "time_period": obj.store_id.time_period,
                "address_link": obj.store_id.address_link,
                "image": obj.store_id.image.url if obj.store_id.image else None
            }
        return None

        
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