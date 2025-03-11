from django.db.utils import IntegrityError
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from combo.models import ComboOffer
from combo.serializers import AdminComboOfferSerializer
from account.permissions import DynamicPermission

@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def combo_offer_crud_operation(request, pk=None):
    """Handles CRUD operations for ComboOffer."""

    # List all combo offers
    if request.method == 'GET' and not pk:
        if not request.user.has_perm('combo.view_combooffer'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        print(ComboOffer._meta.app_label)
        combos = ComboOffer.objects.all()
        serializer = AdminComboOfferSerializer(combos, many=True)
        return Response({'message': 'Combo offers retrieved successfully', 'data': {'combos': serializer.data}}, status=status.HTTP_200_OK)

    # Retrieve a single combo offer by ID
    if request.method == 'GET' and pk:
        if not request.user.has_perm('combo.view_combooffer'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            combo = ComboOffer.objects.get(id=pk)
            serializer = AdminComboOfferSerializer(combo)
            return Response({'message': 'Combo offer retrieved successfully', 'data': {'combo': serializer.data}}, status=status.HTTP_200_OK)
        except ComboOffer.DoesNotExist:
            return Response({'message': 'Combo offer not found'}, status=status.HTTP_404_NOT_FOUND)

    # Create a new combo offer
    if request.method == 'POST':
        if not request.user.has_perm('combo.add_combooffer'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = AdminComboOfferSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({'message': 'Combo offer created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'message': 'A combo offer with this title already exists.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Validation error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # Update a combo offer
    if request.method == 'PATCH':
        if not request.user.has_perm('combo.change_combooffer'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        if not pk:
            return Response({'message': 'Combo offer ID (pk) is required in the URL'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            combo = ComboOffer.objects.get(id=pk)
            serializer = AdminComboOfferSerializer(combo, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Combo offer updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
            return Response({'message': 'Validation error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except ComboOffer.DoesNotExist:
            return Response({'message': 'Combo offer not found'}, status=status.HTTP_404_NOT_FOUND)

    # Delete a combo offer
    if request.method == 'DELETE':
        if not request.user.has_perm('combo.delete_combooffer'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            combo = ComboOffer.objects.get(id=pk)
            combo.delete()
            return Response({'message': 'Combo offer deleted successfully'}, status=status.HTTP_200_OK)
        except ComboOffer.DoesNotExist:
            return Response({'message': 'Combo offer not found'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'message': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)