# api for whos grop is admin will create role and assign a permission


from rest_framework import serializers
from django.contrib.auth.models import Group, Permission
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.decorators import authentication_classes

class GroupPermissionSerializer(serializers.Serializer):
    group_name = serializers.CharField(max_length=255)
    permissions = serializers.ListField(child=serializers.CharField(max_length=255))

    def validate_group_name(self, value):
        if Group.objects.filter(name=value).exists():
            raise serializers.ValidationError("Group name already exists.")
        return value

    @property
    def errors(self):
        errors = super().errors
        # Flatten errors for group_name if it exists
        if "group_name" in errors and isinstance(errors["group_name"], list):
            errors["group_name"] = errors["group_name"][0]
        return errors


    def create(self, validated_data):
        group_name = validated_data['group_name']
        permissions = validated_data['permissions']

        group, _ = Group.objects.get_or_create(name=group_name)

        for permission_name in permissions:
            permission, _ = Permission.objects.get_or_create(codename=permission_name)
            group.permissions.add(permission)

        return group

@api_view(['POST'])
@permission_classes([IsAuthenticated])  
@authentication_classes([JWTAuthentication])
def create_group_and_assign_permissions(request):
    user = request.user
    
    if not user.groups.filter(name='admin').exists():
        return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = GroupPermissionSerializer(data=request.data)
    if serializer.is_valid():
        group_name = serializer.validated_data['group_name']
        permissions_codenames = serializer.validated_data['permissions']
        
        group, created = Group.objects.get_or_create(name=group_name)

        permissions = Permission.objects.filter(codename__in=permissions_codenames)
        if permissions.count() != len(permissions_codenames):
            return Response({'message': 'Some permissions do not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        group.permissions.set(permissions)  
        group.save()
        
        return Response({'message': f'Group "{group_name}" created and permissions assigned successfully.'}, status=status.HTTP_201_CREATED)
    else:
        return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])  
@authentication_classes([JWTAuthentication])
def get_permissions(request):
    user = request.user
    permissions = user.get_all_permissions()
    data = {
        'permissions': permissions
    }
    return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
