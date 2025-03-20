from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import razorpay
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes
import os
from dotenv import load_dotenv
from order.models import Order
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
        if order.coupon_applied:
            # Save coupon usage
            coupon = order.applied_coupon
            # Ensure only one coupon usage per user per coupon
            coupon_usage, created = CouponUsage.objects.get_or_create(
                user=order.customer_id, coupon=coupon,
                defaults={'usage_count': 1}
            )

            if not created:
                coupon_usage.usage_count += 1
                coupon_usage.save()
            print("✅ Coupon usage updated successfully.")    

        return Response({"message": "Payment successful"}, status=status.HTTP_200_OK)
    except razorpay.errors.SignatureVerificationError:
        return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)