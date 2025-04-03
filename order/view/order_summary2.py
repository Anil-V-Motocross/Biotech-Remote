from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from order.models import Order, DeliveryAddress, OrderItem
from account.permissions import DynamicPermission
from rest_framework import serializers
from account.models import Address
from order.serializers import DeliveryAddressSerializer, OrderItemSerializer, OrderSerializer
from store.models import Store
from django.utils import timezone  
from datetime import timedelta

@api_view(['PATCH'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def order_summary(request):
    if request.method == 'PATCH':
        required_permissions = [
            'order.change_order'
        ]
        
        # Check if the user has the required permissions
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        print("user in order summary:", request.user)
        
        # Extract data from the request
        order_id = request.data.get('order_id', None)
        address_id = request.data.get('address_id', None)
        delivery_option = request.data.get('delivery_option', None)

        #New 
        store_id = request.data.get('store_id', None)
        print("selected order:", order_id)
        print("selected address:", address_id)
        print("selected delivery option:", delivery_option)
        print("selected store:", store_id)
        
        # Validate required fields
        if not order_id:
            return Response(data={'message': 'Order id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not address_id:
            return Response(data={'message': 'Address id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not delivery_option:
            return Response(data={'message': 'Delivery option is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Validate the address
        if not Address.objects.filter(id=address_id, user=request.user.id, is_default=True).exists():
            return Response(data={"message": "Address not found."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Fetch the order
        if not Order.objects.filter(id=order_id, customer_id=request.user.id).exists():
            return Response(data={'message': 'Order not found.'}, status=status.HTTP_400_BAD_REQUEST)
        
        order = Order.objects.get(id=order_id, customer_id=request.user.id)
        user_default_address = Address.objects.get(id=address_id, user=request.user.id, is_default=True)
        
        # Delete existing delivery address for this order (if any)
        DeliveryAddress.objects.filter(user_id=request.user.id, order_id=order_id).delete()
        
        # Create a new delivery address
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
            return Response(data={"message": "error", 'errors': delivery_serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        

        # New
        if delivery_option == 'Pick Up Store':
            if not store_id:
                return Response({'message': 'Store id is required for store pickup.'}, status=status.HTTP_400_BAD_REQUEST)

            store = Store.objects.filter(id=store_id).first()
            if not store:
                return Response({'message': 'Store not found.'}, status=status.HTTP_400_BAD_REQUEST)

            order.store_id = store
            order.pickup_deadline = timezone.now() + timedelta(days=7)
            order.delivery_option = 'PickUpStore'
            order.save()
        else:
            # Set Home Delivery Option
            order.delivery_option = delivery_option
            order.save()



        # Update the order's delivery option
        # order.delivery_option = delivery_option
        # order.save()
        
        # Fetch order items
        order_items = OrderItem.objects.filter(order_id=order.id)
        order_items_serializer = OrderItemSerializer(order_items, many=True)
        
        # Prepare the response data
        order_serializer = OrderSerializer(order)
        data = {
            'order': order_serializer.data,
            'order_items': order_items_serializer.data
        }
        
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)