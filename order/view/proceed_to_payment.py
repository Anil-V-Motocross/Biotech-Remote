from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission
from rest_framework import serializers
from order.models import Order
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()



@api_view(['PATCH'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def proceed_to_payment(request):
    if request.method == 'PATCH':
        required_permissions = [
            'order.change_order'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        order_id = request.data.get('order_id', None)
        payment_method = request.data.get('payment_method', None)
        
        if not order_id:
            return Response(data={'message': 'Order id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        if not payment_method:
            return Response(data={'message': 'Payment method is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Order.objects.filter(id=order_id, customer_id=request.user.id).exists():
        # if Order.objects.filter(id=order_id, customer_id=15).exists():
            order = Order.objects.get(id=order_id, customer_id=request.user.id)
            # order = Order.objects.get(id=order_id, customer_id=15)
            order.payment_method = payment_method
            order.save()
            
            if payment_method == 'UPI':
                # Razorpay payment gateway
                import razorpay
                razorpay_client = razorpay.Client(auth=(os.getenv('RAZORPAY_KEY'), os.getenv('RAZORPAY_SECRET')))
                data = {
                    'amount': int(order.grand_total) * 100,
                    'currency': 'INR',
                    "payment_capture": 1,
                    'receipt': order.order_id,
                    'notes': {
                        'customer_id': order.customer_id.bmu
                    }
                }
                razorpay_order = razorpay_client.order.create(data)
                order.razorpay_order_id = razorpay_order.get('id')
                order.save()
                data = {
                    'razorpay_order': razorpay_order
                }
                return Response(razorpay_order)
            elif payment_method == 'Cash':
                return Response(data={'message': 'Payment successful.'}, status=status.HTTP_200_OK)
            else:
                return Response(data={'message': 'Invalid payment method.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={'message': 'Order does not exist.'}, status=status.HTTP_400_BAD_REQUEST)