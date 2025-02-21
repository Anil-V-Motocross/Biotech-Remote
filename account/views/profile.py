from rest_framework import serializers
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission
from rest_framework.response import Response
from account.models import Address, User
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'first_name', 'last_name', 'email', 'date_of_birth', 'gender', 'mobile')
        read_only_fields = ('id', 'mobile')

    first_name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    last_name = serializers.CharField(required=True, allow_null=False, allow_blank=False)
    email = serializers.EmailField(required=True, allow_null=False, allow_blank=False)
    date_of_birth = serializers.DateField(required=True, allow_null=False)
    gender = serializers.CharField(required=True, allow_null=False, allow_blank=False)

    def validate(self, data):
        """
        Ensure required fields are not null or blank during PATCH (partial update).
        """
        request_method = self.context.get('request').method if self.context.get('request') else None

        if request_method == 'PATCH':  # Ensure required fields are not null or blank when updating
            for field in ['first_name', 'last_name', 'email', 'date_of_birth', 'gender']:
                if field in data and (data[field] is None or data[field] == ''):
                    raise serializers.ValidationError({field: f"{field.replace('_', ' ').capitalize()} cannot be null or blank."})

        return data

    def to_representation(self, instance):
        """Modify the representation of the email field in the response."""
        data = super().to_representation(instance)

        email = data.get("email")
        mobile = data.get("mobile")

        if email and "@" in email:
            local_part = email.split("@")[0]
            if local_part == mobile:
                data["email"] = None  # Set email as null in the response

        return data

        
class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model =Address
        fields=('id','first_name','last_name','address', 'state', 'city', 'address_type', 'pincode', 'is_default', 'user')
        read_only_fields = ('id',)
       

@api_view(['GET','PATCH',])
@permission_classes([IsAuthenticated,DynamicPermission])
@authentication_classes([JWTAuthentication])
def profile(request):
    if request.method == 'GET':
        required_permissions = ['account.view_user']
       
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
       
        if User.objects.filter(id=request.user.id).exists():
            user = User.objects.get(id=request.user.id)
            serializer = UserProfileSerializer(user)
            data = {
                "profile": serializer.data
            }
            return Response(data={'message':'success', 'data': data}, status=status.HTTP_200_OK)
        return Response(data={'message':'no user found'}, status=status.HTTP_404_NOT_FOUND)
   
    if request.method == 'PATCH':
       required_permissions = ['account.change_user']
       
       if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
       
       user_id = request.user.id
       
       if User.objects.filter(id=user_id).exists():
            user = User.objects.get(id=user_id)
            serializer = UserProfileSerializer(user, data=request.data.get('profile'), partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
       return Response(data={'message': 'User does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
   
    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)
   
# Manage Address

@api_view(['GET','POST','PATCH','DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def address(request,pk=None):
    if request.method == 'GET' and not pk:
        required_permissions = ['account.view_address']
       
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        address=Address.objects.filter(user_id=request.user.id)
        serializer = AddressSerializer(address, many=True)
        data={
            'address':serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
     
    if request.method == 'GET'and pk:
        required_permissions = ['account.view_address']
       
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
       
        if Address.objects.filter(id=pk, user_id=request.user.id).exists():
            address = Address.objects.get(id=pk, user_id=request.user.id)
            serializer = AddressSerializer(address, many=False)
            data = {
                'address': serializer.data
            }
            return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Address does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
   
    if request.method == 'POST' and not pk:
        required_permissions = ['account.add_address']
       
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
       
        data = request.data
        data['user'] = request.user.id
        serializer = AddressSerializer(data=data)
        if serializer.is_valid():
            if Address.objects.filter(user_id=request.user.id).exists():
                serializer.save()
            else:
                serializer.save(is_default=True)
            return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        elif serializer.errors:
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    if request.method == 'PATCH' and not pk:
        required_permissions = ['account.change_address']
       
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
       
        data = request.data
        if 'is_default' in data:
            del data['is_default']
        address_id = data.get('address_id')
        if not address_id:
            return Response(data={'message': 'Address ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
       
        if Address.objects.filter(id=address_id, user_id=request.user.id).exists():
            address = Address.objects.get(id=address_id, user_id=request.user.id)
            serializer = AddressSerializer(address, data=data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': 'Address does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'PATCH' and pk:
        required_permissions = ['account.change_address']
       
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
       
        if Address.objects.filter(id=pk, user_id=request.user.id).exists():
            # Update all 'is_default' field to False except the one with the given ID
            Address.objects.filter(user_id=request.user.id).update(is_default=False)
            address = Address.objects.get(id=pk, user_id=request.user.id)
            address.is_default = True
            address.save()
            # returl all address of user
            address = Address.objects.filter(user_id=request.user.id)
            serializer = AddressSerializer(address, many=True)
            data = {
                'address': serializer.data
            }
            return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Address does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
   
    if request.method == 'DELETE' and pk:
        required_permissions = ['account.delete_address']
       
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        if Address.objects.filter(id=pk, user_id=request.user.id).exists():
            address = Address.objects.get(id=pk, user_id=request.user.id)
            if address.is_default:
                return Response(data={'message': 'Default address cannot be deleted.'}, status=status.HTTP_400_BAD_REQUEST)
            address.delete()
            return Response(data={'message': 'Address deleted successfully.'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Address does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
   
    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)

