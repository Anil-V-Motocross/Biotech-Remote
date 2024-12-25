from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from attribute.models import PlanterSize
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission
from rest_framework import serializers


class PlanterSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanterSize
        fields = '__all__'

@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def planter_size(request, pk=None):
    if request.method == 'GET' and not pk:
        required_permissions = [
            'attribute.view_plantersize'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        planter_sizes = PlanterSize.objects.all()
        serializer = PlanterSizeSerializer(planter_sizes, many=True)
        data = {
            'planter_sizes': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    if request.method == 'GET' and pk:
        required_permissions = [
            'attribute.view_plantersize'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if PlanterSize.objects.filter(id=pk).exists():
            planter_size = PlanterSize.objects.get(id=pk)
            serializer = PlanterSizeSerializer(planter_size)
            return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Planter Size not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        required_permissions = [
            'attribute.add_plantersize'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PlanterSizeSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'success'}, status=status.HTTP_201_CREATED)
        return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'PATCH':
        required_permissions = [
            'attribute.change_plantersize'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        planter_size_id = request.data.get('planter_size_id', None)

        if not planter_size_id:
            return Response(data={'message': 'Planter Size ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if PlanterSize.objects.filter(id=planter_size_id).exists():
            planter_size = PlanterSize.objects.get(id=planter_size_id)
            serializer = PlanterSizeSerializer(planter_size, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': 'Planter Size not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'DELETE':
        required_permissions = [
            'attribute.delete_plantersize'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        planter_size_id = request.data.get('planter_size_id', None)

        if not planter_size_id:
            return Response(data={'message': 'Planter Size ID is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if PlanterSize.objects.filter(id=planter_size_id).exists():
            PlanterSize.objects.filter(id=planter_size_id).delete()
            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Planter Size not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)