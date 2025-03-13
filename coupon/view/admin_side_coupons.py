from django.utils import timezone
from django.db.models import F
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.db import IntegrityError
from coupon.models import Coupon
from coupon.serializers import CouponAdminSerializer
from account.permissions import DynamicPermission  # Assuming this is your custom permission class

@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def coupon_crud_operation(request, pk=None):
    """CRUD operations for coupons with permission checks."""

    # List all coupons
    if request.method == 'GET' and not pk:
        if not request.user.has_perm('coupon.view_coupon'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        coupons = Coupon.objects.all()
        serializer = CouponAdminSerializer(coupons, many=True)
        return Response({'message': 'Coupons retrieved successfully', 'data': {'coupons': serializer.data}}, status=status.HTTP_200_OK)

    # Retrieve a single coupon by ID
    if request.method == 'GET' and pk:
        if not request.user.has_perm('coupon.view_coupon'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            coupon = Coupon.objects.get(id=pk)
            serializer = CouponAdminSerializer(coupon)
            return Response({'message': 'Coupon retrieved successfully', 'data': {'coupon': serializer.data}}, status=status.HTTP_200_OK)
        except Coupon.DoesNotExist:
            return Response({'message': 'Coupon not found'}, status=status.HTTP_404_NOT_FOUND)

    # Create a new coupon
    if request.method == 'POST':
        if not request.user.has_perm('coupon.add_coupon'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = CouponAdminSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({'message': 'Coupon created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'message': 'Coupon code already exists, please try a different one'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Validation error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # Update a coupon
    if request.method == 'PATCH':

        if not request.user.has_perm('coupon.change_coupon'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        if not pk:
            return Response({'message': 'Coupon ID (pk) is required in the URL'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            coupon = Coupon.objects.get(id=pk)
            serializer = CouponAdminSerializer(coupon, data=request.data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Coupon updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
            return Response({'message': 'Validation error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        except Coupon.DoesNotExist:
            return Response({'message': 'Coupon not found'}, status=status.HTTP_404_NOT_FOUND)

    # Delete a coupon
    if request.method == 'DELETE':
        if not request.user.has_perm('coupon.delete_coupon'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            coupon = Coupon.objects.get(id=pk)
            coupon.delete()
            return Response({'message': 'Coupon deleted successfully'}, status=status.HTTP_200_OK)
        except Coupon.DoesNotExist:
            return Response({'message': 'Coupon not found'}, status=status.HTTP_404_NOT_FOUND)
