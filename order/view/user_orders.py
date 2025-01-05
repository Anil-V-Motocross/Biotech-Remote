from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from order.models import Order
from rest_framework import serializers
from account.permissions import DynamicPermission

# Serializer for Order model
class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['order_id', 'date', 'grand_total', 'payment_method']

@api_view(['GET'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def user_orders(request, customer_id):
    if request.method == 'GET':
        required_permissions = ['order.view_order']

        if not all(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if Order.objects.filter(customer_id=customer_id).exists():
            user_orders = Order.objects.filter(customer_id=customer_id)

            serializer = OrderSerializer(user_orders, many=True)
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        return Response(data={'message': 'Order does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
