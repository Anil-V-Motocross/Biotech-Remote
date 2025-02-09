from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from order.models import Order
from account.permissions import DynamicPermission

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'order_id', 'date', 'grand_total', 'payment_method']

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
        
        orders = Order.objects.filter(customer_id=request.user.id).all()
        serializer = OrderSerializer(orders, many=True)
        data = {
            'orders': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    return Response(data={'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)