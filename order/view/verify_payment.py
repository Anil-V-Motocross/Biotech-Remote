from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
import razorpay
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes

@api_view(['POST'])
@authentication_classes([JWTAuthentication])
def verify_payment(request):
    """ Verify payment signature from Razorpay """
    data = request.data
    try:
        razorpay_client = razorpay.Client(auth=('rzp_test_zu1D9WznwNYRVG', 'euJDxcFeXHfUuj56RJOww34Q'))
        razorpay_client.utility.verify_payment_signature(data)
        return Response({"message": "Payment successful"}, status=status.HTTP_200_OK)
    except razorpay.errors.SignatureVerificationError:
        return Response({"error": "Payment verification failed"}, status=status.HTTP_400_BAD_REQUEST)