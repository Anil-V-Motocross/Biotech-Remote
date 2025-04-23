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
from decimal import Decimal
from django.db import transaction as db_transaction
from wallet.models import Transaction, Wallet


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

            total_amount = Decimal(order.grand_total)
            
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
                    'razorpay_order': razorpay_order,
                    'order_id':order.id
                }
                return Response(data)

            elif payment_method == 'Wallet':
                wallet = request.user.wallet
                if not wallet.is_active:
                    return Response({'message': 'Wallet is inactive.'}, status=status.HTTP_403_FORBIDDEN)

                with db_transaction.atomic():
                    if wallet.has_sufficient_balance(total_amount):
                        wallet.debit(total_amount)

                        Transaction.objects.create(
                            wallet=wallet,
                            transaction_type="DEBIT",
                            amount=total_amount,
                            status="COMPLETED",
                            description=f"Wallet payment for Order #{order.id}"
                        )

                        return Response({'message': 'Payment successful via wallet.'}, status=status.HTTP_200_OK)

                    else:
                        wallet_amount = wallet.balance
                        remaining_amount = total_amount - wallet_amount

                        # Debit wallet fully
                        wallet.debit(wallet_amount)
                        Transaction.objects.create(
                            wallet=wallet,
                            transaction_type="DEBIT",
                            amount=wallet_amount,
                            status="COMPLETED",
                            description=f"Partial wallet payment for Order #{order.id}"
                        )

                        # Proceed with Razorpay for remaining
                        import razorpay
                        razorpay_client = razorpay.Client(auth=(os.getenv('RAZORPAY_KEY'), os.getenv('RAZORPAY_SECRET')))
                        data = {
                            'amount': int(remaining_amount * 100),  # in paise
                            'currency': 'INR',
                            'payment_capture': 1,
                            'receipt': order.order_id,
                            'notes': {
                                'customer_id': order.customer_id.bmu
                            }
                        }
                        razorpay_order = razorpay_client.order.create(data)
                        order.razorpay_order_id = razorpay_order.get('id')
                        order.save()

                        return Response({
                            'message': 'Wallet partially used. Please complete remaining payment via UPI.',
                            'wallet_debited': str(wallet_amount),
                            'razorpay_order': razorpay_order,
                            'order_id': order.id
                        }, status=status.HTTP_206_PARTIAL_CONTENT)

            elif payment_method == 'Cash':
                return Response(data={'message': 'Payment successful.'}, status=status.HTTP_200_OK)
            else:
                return Response(data={'message': 'Invalid payment method.'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(data={'message': 'Order does not exist.'}, status=status.HTTP_400_BAD_REQUEST)