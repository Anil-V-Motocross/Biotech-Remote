from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from wallet.models import Wallet, Transaction
from wallet.serializers import TransactionSerializer

@api_view(['GET'])
@permission_classes([IsAuthenticated])   
@authentication_classes([JWTAuthentication])
def wallet_details(request):
    if request.method == 'GET':
        required_permissions = ['wallet.view_wallet']
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            wallet = Wallet.objects.get(user=request.user)
            transactions = Transaction.objects.filter(wallet=wallet).order_by('-created_at')[:10]  # Latest 10 transactions
            serializer = TransactionSerializer(transactions, many=True)

            data = {
                'balance': wallet.balance,
                'transactions': serializer.data
            }
            return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
        
        except Wallet.DoesNotExist:
            return Response(data={'message': 'Wallet not found.'}, status=status.HTTP_404_NOT_FOUND)

    return Response(data={'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)
