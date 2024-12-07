from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from attribute.models import Size
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission
from rest_framework import serializers


class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = '__all__'


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated,DynamicPermission])
@authentication_classes([JWTAuthentication])
def size(request):
    if request.method == 'GET':
        required_permissions = [
            'attribute.view_size'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        sizes = Size.objects.all()
        serializer = SizeSerializer(sizes, many=True)
        data = {
            'sizes': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        required_permissions = [
            'attribute.add_size'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SizeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'success'}, status=status.HTTP_201_CREATED)
        return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'PATCH':
        required_permissions = [
            'attribute.change_size'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        size_id = request.data.get('size_id', None)
        if not size_id:
            return Response(data={'message': 'size_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        size = Size.objects.get(id=size_id)
        serializer = SizeSerializer(size, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        required_permissions = [
            'attribute.delete_size'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        size_id = request.data.get('size_id', None)
        if not size_id:
            return Response(data={'message': 'size_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Size.objects.filter(id=size_id).exists():
            Size.objects.get(id=size_id).delete()
            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
        
        return Response(data={'message': 'size_id does not exist.'}, status=status.HTTP_400_BAD_REQUEST)