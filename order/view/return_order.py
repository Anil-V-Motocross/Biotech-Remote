from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from rest_framework_simplejwt.authentication import JWTAuthentication
from order.models import Order, OrderStatus, OrderItem


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def request_return(request, order_id):
    user = request.user
    try:
        order = Order.objects.get(id=order_id, customer_id=user)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found or unauthorized access.'}, status=status.HTTP_404_NOT_FOUND)

    # Check if latest status is DELIVERED
    latest_status = order.status_history.first()
    if not latest_status or latest_status.status != 'DELIVERED':
        return Response({'error': 'Return applicable only after delivery.'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if within 7 days from delivered date
    delivery_date = latest_status.timestamp
    if timezone.now() > delivery_date + timedelta(days=7):
        return Response({'error': 'Return window has expired (7 days).'}, status=status.HTTP_400_BAD_REQUEST)

    # ✅ Check if any product in the order is of type "plant"
    order_items = OrderItem.objects.filter(order_id=order)
    for item in order_items:
        if item.product_id.product_id.type == 'plant':
            return Response({'error': 'Orders containing plants cannot be returned.'}, status=status.HTTP_400_BAD_REQUEST)


    # Check if return already requested
    if order.status_history.filter(status='RETURN_REQUESTED').exists():
        return Response({'error': 'Return already requested for this order.'}, status=status.HTTP_400_BAD_REQUEST)

    # Save return request
    OrderStatus.objects.create(
        order=order,
        status='RETURN_REQUESTED',
        notes=request.data.get('notes', '')
    )

    return Response({'message': 'Return request submitted successfully.'}, status=status.HTTP_200_OK)
