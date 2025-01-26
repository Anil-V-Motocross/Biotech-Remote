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
        fields=('id', 'first_name','last_name', 'email', 'date_of_birth','gender', 'mobile', 'user_address')
        read_only_fields = ('id', 'mobile')
        
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
        fields=('user','id','address','city','state','address_type','pincode')
       

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
       
       user_id = request.data.get('user_id')
       if not user_id:
            return Response(data={'message': 'User ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
       
       if User.objects.filter(id=user_id).exists():
            user = User.objects.get(id=user_id)
            serializer = UserProfileSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
       return Response(data={'message': 'User does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
   
    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)
   
 
       
       
 #-------------------------adddress------------------------


@api_view(['GET','POST','PATCH','DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def add_address(request,pk=None):
    if request.method == 'GET' and not pk:
        required_permissions = ['account.view_address']
       
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        address=Address.objects.all()
        serializer = AddressSerializer(address, many=True)
        data={
            'address':serializer.data
        }
        return Response(data, status=status.HTTP_200_OK)
     
           
    if request.method == 'GET'and pk:
        required_permissions = ['account.view_address']
       
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
       
        address = Address.objects.filter(user_id=pk)
        serializer = AddressSerializer(address, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
   
    if request.method == 'POST':
 
        required_permissions = ['account.add_address']
       
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
       
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            # Check if this is the first address for the user
            user = request.user
            has_existing_addresses = Address.objects.filter(user=user).exists()
           
            # Save the new address
            address = serializer.save(user=user)
           
            # Set as default if it's the first address
            if not has_existing_addresses:
                address.is_default = True
                address.save()
           
            return Response(data={
                'message': 'Address added successfully.',
                'data': AddressSerializer(address).data
            }, status=status.HTTP_201_CREATED)
       
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
       
 


    if request.method == 'PATCH':
        required_permissions = ['account.change_address']
       
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
       
        address_id = request.data.get('address_id')
        if not address_id:
            return Response(data={'message': 'Address ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
       
        if Address.objects.filter(id=address_id).exists():
            address = Address.objects.get(id=address_id)
            serializer = AddressSerializer(address, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': 'Address does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
   
   
    if request.method == 'DELETE':
        required_permissions = ['account.delete_address']
       
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        if Address.objects.filter(id=pk).exists():
            address = Address.objects.get(id=pk)
            address.delete()
            return Response(data={'message': 'Address deleted successfully.'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Address does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
   
    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)

