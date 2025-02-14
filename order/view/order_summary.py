from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from order.models import Order, DeliveryAddress
from account.permissions import DynamicPermission
from rest_framework import serializers
from account.models import Address


class DeliveryAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeliveryAddress
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'total_price', 'total_discount', 'grand_total']

@api_view(['PATCH'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def order_summary(request):
    if request.method == 'PATCH':
        required_permissions = [
            'order.change_order'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        order_id = request.data.get('order_id', None)
        address_id = request.data.get('address_id', None)
        delivery_option = request.data.get('delivery_option', None)
        if not order_id:
            return Response(data={'message': 'Order id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not address_id:
            return Response(data={'message': 'Address id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not delivery_option:
            return Response(data={'message': 'Delivery option is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if not Address.objects.filter(id=address_id, user=request.user.id, is_default=True).exists():
            return Response(data={"message": "Address not found."})
        
        if Order.objects.filter(id=order_id, customer_id=request.user.id).exists():
            order = Order.objects.get(id=order_id, customer_id=request.user.id)
            user_default_address = Address.objects.get(id=address_id, user=request.user.id, is_default=True)
            
            if DeliveryAddress.objects.filter(user_id=request.user.id, order_id=order_id).exists():
                delivery_address = DeliveryAddress.objects.filter(user_id=request.user.id, order_id=order_id)
                delivery_address.delete()
            
            delivery_address_data = {
                "first_name": user_default_address.first_name,
                "last_name": user_default_address.last_name,
                "address": user_default_address.address,
                "state": user_default_address.state,
                "city": user_default_address.city,
                "pincode": user_default_address.pincode,
                "address_type": user_default_address.address_type,
                "user_id": request.user.id,  # FK object, not just ID
                "order_id": order.id,  # FK object, not just ID
            }
            delivery_serializer = DeliveryAddressSerializer(data=delivery_address_data)
            if delivery_serializer.is_valid():
                delivery_serializer.save()
            else:
                return Response(data={"message": "error", 'errors': delivery_serializer.errors})
            
            order.delivery_option = delivery_option
            order.save()
            
            serializer = OrderSerializer(order)
            data = {
                'orders': serializer.data
            }
            return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
        else:
            return Response(data={'message': 'Order not found.'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)