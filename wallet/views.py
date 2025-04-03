from rest_framework import generics, permissions, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Wallet, Transaction
from .serializers import WalletSerializer, TransactionSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication

class WalletDetailView(generics.RetrieveAPIView):
    """
    Retrieve the authenticated user's wallet details.
    """
    serializer_class = WalletSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        """
        Get the wallet for the authenticated user.
        If not found, return an error response.
        """
        user = self.request.user
        wallet = Wallet.objects.filter(user=user).first()
        if not wallet:
            return Response({"message": "Wallet not found", "data": None}, status=status.HTTP_404_NOT_FOUND)
        return wallet

    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve method to format response.
        """
        wallet = self.get_object()
        if isinstance(wallet, Response):  
            return wallet
        
        serializer = self.get_serializer(wallet)
        return Response({"message": "Wallet details retrieved successfully", "data": serializer.data}, status=status.HTTP_200_OK)


class TransactionListView(generics.ListAPIView):
    """
    List all transactions for the authenticated user's wallet.
    """
    serializer_class = TransactionSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        """
        Get transactions only for the authenticated user's wallet.
        Handle case where wallet does not exist.
        """
        user = self.request.user
        wallet = Wallet.objects.filter(user=user).first()
        if not wallet:
            return None
        return wallet.transactions.all()

    def list(self, request, *args, **kwargs):
        """
        Override list method to format response.
        """
        try:
            user = self.request.user
            wallet = Wallet.objects.filter(user=user).first() 

            if not wallet:
                return Response({"message": "Wallet not found", "data": []}, status=status.HTTP_404_NOT_FOUND)
            queryset = self.get_queryset()
            if queryset is None:
                return Response({"message": "Wallet not found"}, status=status.HTTP_404_NOT_FOUND)
            
            serializer = self.get_serializer(queryset, many=True)
            return Response({"message": "Transactions retrieved successfully", "data": {"balance": wallet.balance, "transactions":serializer.data}}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"message": "Error retrieving transactions", "data": str(e)}, status=status.HTTP_400_BAD_REQUEST)
