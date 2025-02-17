import requests
import rest_framework.decorators
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from order.models import Order
from rest_framework import serializers
from account.permissions import DynamicPermission
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from account.permissions import DynamicPermission


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

@api_view(['GET', 'POST', 'PATCH'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def order(request, pk=None):
    if request.method == 'GET' and not pk:
        required_permissions = [
            'order.view_order'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        orders = Order.objects.all()
        serializer = OrderSerializer(orders, many=True)
        return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
    
    if request.method == 'GET' and pk:
        required_permissions = [
            'order.view_order'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if Order.objects.filter(id=pk).exists():
            order = Order.objects.get(id=pk)
            serializer = OrderSerializer(order)
            return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Order does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'POST':
        required_permissions = [
            'order.add_order'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OrderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'success'}, status=status.HTTP_201_CREATED)
        if serializer.errors:
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    if request.method == 'PATCH':
        required_permissions = [
            'order.change_order'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        order_id = request.data.get('id')

        if not order_id:
            return Response(data={'message': 'Order ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Order.objects.filter(id=order_id).exists():
            order = Order.objects.get(id=order_id)
            serializer = OrderSerializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
            if serializer.errors:
                return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': 'Order does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        
    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def admin_user_orders(request, user_id):
    required_permissions = [
            'order.view_order'
        ]

    if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

    if not User.objects.filter(id=user_id).exists():
        return Response(data={'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

    orders = Order.objects.filter(customer_id=user_id)
    serializer = OrderSerializer(orders, many=True)

    return Response(data={'message': 'success', 'orders': serializer.data}, status=status.HTTP_200_OK)            
