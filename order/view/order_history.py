from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from order.models import Order, DeliveryAddress
from account.permissions import DynamicPermission

class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = ['first_name', 'last_name', 'address', 'state', 'city', 'pincode', 'address_type']

class OrderSerializer(serializers.ModelSerializer):
    delivery_address = serializers.SerializerMethodField()
    product_details  = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'order_id', 'date', 'total_price', 'total_discount', 'tracking_id', 'grand_total', 
                  'payment_method', 'customer_name', 'delivery_option', 'status', 'razorpay_order_id', 'delivery_address', 'product_details']

    def get_delivery_address(self, obj):
        try:
            delivery_address = obj.order_address.first()  # Assuming one delivery address per order
            return DeliveryAddressSerializer(delivery_address).data if delivery_address else None
        except DeliveryAddress.DoesNotExist:
            return None

    def get_product_details(self, obj):
        """
        Returns the first product's name and image from the order, if available.
        """
        order_item = obj.orderitem_set.first()  # Get the first order item
        if order_item:
            return {
                "product_name": order_item.product_id.name if order_item.product_id else None,
                "product_image": order_item.image.url if order_item.image else None
            }
        return None
    
    def get_status(self, obj):
        """ Fetch the latest status of the order """
        latest_status = obj.status_history.first()  # Get the latest status based on ordering in Meta class
        return latest_status.status if latest_status else None

# @api_view(['GET'])
# @permission_classes([IsAuthenticated, DynamicPermission])   
# @authentication_classes([JWTAuthentication])
# def order_history(request):
#     if request.method == 'GET':
#         required_permissions = [
#             'order.view_order'
#         ]
        
#         if not any(request.user.has_perm(perm) for perm in required_permissions):
#             return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
#         orders = Order.objects.filter(customer_id=request.user.id).order_by('-id') 
#         serializer = OrderSerializer(orders, many=True)
#         data = {
#             'orders': serializer.data
#         }
#         return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
#     return Response(data={'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, DynamicPermission])   
@authentication_classes([JWTAuthentication])
def order_history(request):
    if request.method == 'GET':
        required_permissions = [
            'order.view_order'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        # Filter orders for the current user
        orders = Order.objects.filter(customer_id=request.user.id).order_by('-id')

        # Exclude orders where the latest OrderStatus is "INITIATED"
        filtered_orders = [
            order for order in orders
            if not order.status_history.first() or order.status_history.first().status != 'INITIATED'
        ]

        serializer = OrderSerializer(filtered_orders, many=True)
        data = {
            'orders': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    return Response(data={'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)
