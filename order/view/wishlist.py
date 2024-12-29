from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from order.models import Wishlist
from account.permissions import DynamicPermission
from rest_framework import serializers

class WishlistSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wishlist
        fields = '__all__'
        

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def wishlist(request, pk=None):
    if request.method == 'GET':
        required_permissions = [
            'order.view_wishlist'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        wishlists = Wishlist.objects.filter(user_id=request.user.id).all()
        serializer = WishlistSerializer(wishlists, many=True)
        data = {
            'wishlists': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        required_permissions = [
            'order.add_wishlist'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        data = {
            'user_id': request.user.id,
            'product_id': request.data.get('prod_id'),
        }
        serializer = WishlistSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'success'}, status=status.HTTP_201_CREATED)
        return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE' and pk:
        required_permissions = [
            'order.delete_wishlist'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if Wishlist.objects.filter(id=pk, user_id=request.user.id).exists():
            wishlist = Wishlist.objects.get(id=pk, user_id=request.user.id)
            wishlist.delete()
            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Wishlist does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    