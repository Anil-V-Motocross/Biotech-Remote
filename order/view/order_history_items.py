from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from order.models import Order, OrderItem, OrderStatus
from account.permissions import DynamicPermission
from rest_framework import serializers

class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product_id.name', read_only=True)
    class Meta:
        model = OrderItem
        fields = '__all__'
        extra_fields = ['product_name']

@api_view(['GET'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def order_history_items(request, order_id):
    if request.method == 'GET':
        required_permissions = [
            'order.view_order', 'order.view_orderitem'
        ]
        
        if not all(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if Order.objects.filter(id=order_id, customer_id=request.user.id).exists():
            order_items = OrderItem.objects.filter(order_id=order_id)
            serializer = OrderItemSerializer(order_items, many=True)
            tracking_updates = OrderStatus.objects.filter(order_id=order_id).exclude(status='INITIATED').order_by('timestamp')
            tracking_data = [
                {
                    'status': update.get_status_display(),
                    'timestamp': update.timestamp,
                    'notes': update.notes
                }
                for update in tracking_updates
            ]
            data = {
                'order_items': serializer.data,
                'tracking_updates': tracking_data
            }
            return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Order does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(data={'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)