from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from coupon.models import Coupon
from order.models import Order


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def validate_coupon(request):
    """Validate if the coupon is applicable before applying."""
    coupon_code = request.data.get('coupon_code')
    total_price = request.data.get('total_price')  # Price before discount
    
    if not coupon_code:
        return Response({'message': 'Coupon code is required.'}, status=status.HTTP_400_BAD_REQUEST)

    coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()
    
    if not coupon:
        return Response({'message': 'Invalid or expired coupon.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if minimum order value condition is met
    if total_price < coupon.minimum_order_value:
        return Response({'message': f'Coupon requires minimum order value of {coupon.minimum_order_value}.'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Check if user has already used the coupon (if it's a one-time use coupon)
    if coupon.is_one_time_use and Order.objects.filter(customer=request.user, applied_coupon=coupon).exists():
        return Response({'message': 'This coupon has already been used.'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'message': 'Coupon is valid.', 'discount_amount': coupon.discount_amount}, status=status.HTTP_200_OK)
