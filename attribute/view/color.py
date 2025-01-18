from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from attribute.models import Color
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission
from rest_framework import serializers


class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = '__all__'
        
    # def validate function for color_name
    def to_internal_value(self, data):
        # Convert color_name to lowercase before any other validation happens
        if 'color_name' in data:
            data['color_name'] = data['color_name'].lower()
        return super().to_internal_value(data)
    

@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def color(request, pk=None):
    if request.method == 'GET' and not pk:
        required_permissions = [
            'attribute.view_color'
        ]
        
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        colors = Color.objects.all()
        serializer = ColorSerializer(colors, many=True)
        data = {
            'colors': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    if request.method == 'GET' and pk:
        required_permissions = [
            'attribute.view_color'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if Color.objects.filter(id=pk).exists():
            color = Color.objects.get(id=pk)
            serializer = ColorSerializer(color)
            data = {
                'color': serializer.data
            }
            return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
        return Response(data={'message': 'color not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        required_permissions = [
            'attribute.add_color'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        data = request.data
        serializer = ColorSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'success'}, status=status.HTTP_201_CREATED)
        return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'PATCH':
        required_permissions = [
            'attribute.change_color'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        color_id = request.data.get('color_id', None)

        if not color_id:
            return Response({'message': 'color_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Color.objects.filter(id=color_id).exists():
            color = Color.objects.get(id=color_id)
            data = request.data
            serializer = ColorSerializer(color, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': 'color not found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'DELETE':
        required_permissions = [
            'attribute.delete_color'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        color_id = request.data.get('color_id', None)

        if not color_id:
            return Response({'message': 'color_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Color.objects.filter(id=color_id).exists():
            Color.objects.filter(id=color_id).delete()
            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'color not found'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)