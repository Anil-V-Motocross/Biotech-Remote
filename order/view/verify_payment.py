from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import razorpay
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes
import os
from dotenv import load_dotenv
from order.models import Order, OrderStatus, Cart, OrderItem
from coupon.models import CouponUsage


# Load .env file
load_dotenv()

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def verify_payment(request):
    """ Verify payment signature from Razorpay """
    data = request.data
    print("Verify payment data:", data)
    try:
        order_id = data.get('order_id')
        if not order_id:
            return Response({"error": "Order ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        razorpay_client = razorpay.Client(auth=(os.getenv('RAZORPAY_KEY'), os.getenv('RAZORPAY_SECRET')))
        razorpay_client.utility.verify_payment_signature(data)
        
        order = Order.objects.get(id=order_id)

        order_status = OrderStatus.objects.create(order=order, status="PROCESSING")

        if order.coupon_applied and order.applied_coupon:
            # Save coupon usage
            coupon = order.applied_coupon
            # Ensure only one coupon usage per user per coupon
            coupon_usage, created = CouponUsage.objects.get_or_create(
                user=order.customer_id, 
                coupon=coupon,
                order=order
            )

            if created:
                print(f"✅ Coupon '{coupon.code}' usage recorded for user {order.customer_id}.")
            else:
                print(f"⚠️ Coupon '{coupon.code}' was already used in this order.")    

        cart_items = set(Cart.objects.filter(user_id=request.user.id).values_list('product_id', flat=True))
        order_items = set(OrderItem.objects.filter(order_id=order).values_list('product_id', flat=True))

        # Check if all order items exactly match the cart items
        if order_items == cart_items:  
            Cart.objects.filter(user_id=request.user.id).delete()       

        return Response({"message": "Payment successful"}, status=status.HTTP_200_OK)
    except razorpay.errors.SignatureVerificationError:
        return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)