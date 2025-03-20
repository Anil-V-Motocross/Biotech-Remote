from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from .models import BTCoinsWallet, BTCoinsTransaction, BTCoinsSettings
from .serializers import BTCoinsWalletSerializer, BTCoinsTransactionSerializer,BTCoinsSettingsAdminSerializer
from account.permissions import DynamicPermission

# ***** User Side *****
class UserWalletView(generics.RetrieveAPIView):
    """ Fetch logged-in user's wallet details """
    serializer_class = BTCoinsWalletSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]


    def get_object(self):
        try:
            return BTCoinsWallet.objects.get(user=self.request.user)
        except BTCoinsWallet.DoesNotExist:
            self.handle_error('Wallet not found', status.HTTP_404_NOT_FOUND)
        except Exception as e:
            self.handle_error(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

    def handle_error(self, message, status_code):
        """ Custom error handler """
        response = Response({'success': False, 'error': message}, status=status_code)
        self.response = response
        raise Exception(response)
    

class UserTransactionsView(generics.ListAPIView):
    """ Retrieve logged-in user's transactions """
    serializer_class = BTCoinsTransactionSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def list(self, request, *args, **kwargs):
        """ Custom response format to always include success & data keys """
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response({"success": True, "data": serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return self.handle_error(str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_queryset(self):
        """ Get only the transactions of the logged-in user """
        return BTCoinsTransaction.objects.filter(user=self.request.user).order_by('-created_at')

    def handle_error(self, message, status_code):
        """ Custom error handler """
        return Response({"success": False, "error": message}, status=status_code)


# *****  Admin Side *****
class BTCoinsSettingsView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handles retrieving, updating, and deleting BTCoins settings.
    Only staff users can access these endpoints.
    """
    serializer_class = BTCoinsSettingsAdminSerializer
    permission_classes = [IsAuthenticated, DynamicPermission]
    authentication_classes = [JWTAuthentication]

    def get_object(self):
        """Fetch the settings object or create one if it doesn't exist"""
        return BTCoinsSettings.get_settings()

    def get(self, request, *args, **kwargs):
        """Retrieve settings (staff-only)"""
        if not request.user.is_staff:
            return Response({'message': 'You do not have permission to view settings.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            settings = self.get_object()
            serializer = self.get_serializer(settings)
            return Response({'message': 'Settings retrieved successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'message': 'Error retrieving settings', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def patch(self, request, *args, **kwargs):
        """Update settings (staff-only)"""
        if not request.user.is_staff:
            return Response({'message': 'You do not have permission to update settings.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            settings = self.get_object()
            serializer = self.get_serializer(settings, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Settings updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
            return Response({'message': 'Validation error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'message': 'Error updating settings', 'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def delete(self, request, *args, **kwargs):
    #     """Prevent deletion (override to return a message)"""
    #     if not request.user.is_staff:
    #         return Response({'message': 'You do not have permission to update settings.'}, status=status.HTTP_403_FORBIDDEN)
    #     return Response({'message': 'Settings cannot be deleted.'}, status=status.HTTP_403_FORBIDDEN)
