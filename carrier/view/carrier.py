from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from carrier.models import Carrier
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission
from rest_framework import serializers


class CarrierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Carrier
        fields = '__all__'


@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def carrier(request, pk=None):
    if request.method == 'GET' and not pk:
        required_permissions = [
            'carrier.view_carrier'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        carrier = Carrier.objects.all()
        serializer = CarrierSerializer(carrier, many=True)
        data = {
            'carrier': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    if request.method == 'GET' and pk:
        required_permissions = [
            'carrier.view_carrier'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        carrier_id = request.data.get('carrier_id')

        if not carrier_id:
            return Response(data={'message': 'Carrier ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if Carrier.objects.filter(id=carrier_id).exists():
            carrier = Carrier.objects.get(id=carrier_id)
            serializer = CarrierSerializer(carrier)
            data = {
                'carrier': serializer.data
            }
            return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Carrier not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        required_permissions = [
            'carrier.add_carrier'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CarrierSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'success'}, status=status.HTTP_201_CREATED)
        return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'PATCH':
        required_permissions = [
            'carrier.change_carrier'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        carrier_id = request.data.get('carrier_id')

        if not carrier_id:
            return Response(data={'message': 'Carrier ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if Carrier.objects.filter(id=carrier_id).exists():
            carrier = Carrier.objects.get(id=carrier_id)
            serializer = CarrierSerializer(carrier, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': 'Carrier not found.'}, status=status.HTTP_404_NOT_FOUND)
        
    if request.method == 'DELETE':
        required_permissions = [
            'carrier.delete_carrier'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        carrier_id = request.data.get('carrier_id')

        if not carrier_id:
            return Response(data={'message': 'Carrier ID is required.'}, status=status.HTTP_400_BAD_REQUEST)

        if Carrier.objects.filter(id=carrier_id).exists():
            carrier = Carrier.objects.get(id=carrier_id)
            carrier.delete()
            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Carrier not found.'}, status=status.HTTP_404_NOT_FOUND)
    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)



# Public APIs
@api_view(['GET'])
def public_carrier(request):
    if request.method == 'GET':
        carrier = Carrier.objects.all()
        serializer = CarrierSerializer(carrier, many=True)
        data = {
            'carrier': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)