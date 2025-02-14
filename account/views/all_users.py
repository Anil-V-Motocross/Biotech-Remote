from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.models import User
from rest_framework import serializers
from account.permissions import DynamicPermission

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'profile_picture', 'first_name', 'last_name', 'email', 'date_of_birth', 'mobile', 'bmu', 'referal_code']

@api_view(['GET'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def all_users(request, pk=None):
    if request.method == 'GET' and not pk:
        required_permissions = [
            'account.view_user'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        users = User.objects.filter(is_superuser=False).all()
        serializer = UserSerializer(users, many=True)
        data = {
            'users': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    if request.method == 'GET' and pk:
        required_permissions = [
            'account.view_user'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if User.objects.filter(id=pk).exists():
            user = User.objects.get(id=pk)
            serializer = UserSerializer(user)
            return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(data={'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)