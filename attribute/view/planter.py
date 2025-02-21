from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from attribute.models import Planter
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission
from rest_framework import serializers


class PlanterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planter
        fields = '__all__'
        
    def to_internal_value(self, data):
        data = data.copy()  # This will ensure the data is mutable
        if 'name' in data:
            data['name'] = data['name'].lower()
        return super().to_internal_value(data)

@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def planter(request, pk=None):
    if request.method == 'GET' and not pk:
        required_permissions = [
            'attribute.view_planter'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        filter_params = {}
        planter_size = request.query_params.get('planter_size', None)
        
        if planter_size:
            filter_params['planter_size'] = planter_size
        
        planters = Planter.objects.filter(**filter_params).all()
        
        # planters = Planter.objects.all()
        serializer = PlanterSerializer(planters, many=True)
        data = {
            'planters': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    if request.method == 'GET' and pk:
        required_permissions = [
            'attribute.view_planter'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if Planter.objects.filter(id=pk).exists():
            planter = Planter.objects.get(id=pk)
            serializer = PlanterSerializer(planter)
            data = {
                'planter': serializer.data
            }
            return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Planter not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        required_permissions = [
            'attribute.add_planter'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PlanterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'success'}, status=status.HTTP_201_CREATED)
        return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'PATCH':
        required_permissions = [
            'attribute.change_planter'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        planter_id = request.data.get('planter_id', None)
        
        if not planter_id:
            return Response(data={'message': 'Planter ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Planter.objects.filter(id=planter_id).exists():
            planter = Planter.objects.get(id=planter_id)
            serializer = PlanterSerializer(planter, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': 'Planter not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'DELETE':
        required_permissions = [
            'attribute.delete_planter'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        planter_id = request.data.get('planter_id', None)
        
        if not planter_id:
            return Response(data={'message': 'Planter ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        
        if Planter.objects.filter(id=planter_id).exists():
            Planter.objects.filter(id=planter_id).delete()
            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Planter not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)