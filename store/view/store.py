from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from store.models import Store
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission
from rest_framework import serializers

class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = '__all__'

@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def store(request, pk=None):
    if request.method == 'GET' and not pk:
        required_permissions = [
            'store.view_store'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        stores = Store.objects.all()
        serializer = StoreSerializer(stores, many=True)
        data = {
            'stores': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    if request.method == 'GET' and pk:
        required_permissions = [
            'store.view_store'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if Store.objects.filter(id=pk).exists():
            store = Store.objects.get(id=pk)
            serializer = StoreSerializer(store)
            data = {
                'store': serializer.data
            }
            return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Store not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        required_permissions = [
            'store.add_store'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = StoreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'PATCH' and pk:
        required_permissions = [
            'store.change_store'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        store_id = request.data.get('store_id')
        if not store_id:
            return Response(data={'message': 'Store ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Store.objects.filter(id=store_id).exists():
            store = Store.objects.get(id=store_id)
            serializer = StoreSerializer(instance=store, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': 'Store not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'DELETE' and pk:
        required_permissions = [
            'store.delete_store'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        store_id = request.data.get('store_id')
        if not store_id:
            return Response(data={'message': 'Store ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Store.objects.filter(id=store_id).exists():
            store = Store.objects.get(id=store_id)
            store.delete()
            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Store not found.'}, status=status.HTTP_404_NOT_FOUND)

    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)


# Publiv APIs
@api_view(['GET'])
def store_list(request):
    if request.method == 'GET':
        stores = Store.objects.all()
        serializer = StoreSerializer(stores, many=True)
        data = {
            'stores': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)