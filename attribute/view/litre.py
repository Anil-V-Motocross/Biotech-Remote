from rest_framework import serializers, status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from attribute.models import Litre

class LitreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Litre
        fields = '__all__'

@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated])
@authentication_classes([JWTAuthentication])
def litre(request, pk=None):
    if request.method == 'GET' and not pk:
        required_permissions = [
            'attribute.view_litre'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        litres = Litre.objects.all()
        serializer = LitreSerializer(litres, many=True)
        return Response({'message': 'success', 'data': {'litres': serializer.data}}, status=status.HTTP_200_OK)
    
    if request.method == 'GET' and pk:
        required_permissions = [
            'attribute.view_litre'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if Litre.objects.filter(id=pk).exists():
            litre = Litre.objects.get(id=pk)
            serializer = LitreSerializer(litre)
            return Response({'message': 'success', 'data': {'litre': serializer.data}}, status=status.HTTP_200_OK)
        return Response({'message': 'Litre does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'POST':
        required_permissions = [
            'attribute.add_litre'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = LitreSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'success'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'PATCH':
        required_permissions = [
            'attribute.change_litre'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        litre_id = request.data.get('litre_id')
        if not litre_id:
            return Response({'message': 'Litre id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Litre.objects.filter(id=litre_id).exists():
            litre = Litre.objects.get(id=litre_id)
            serializer = LitreSerializer(litre, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'success'}, status=status.HTTP_200_OK)
            return Response({'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Litre does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE':
        required_permissions = [
            'attribute.delete_litre'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        litre_id = request.data.get('litre_id')
        if not litre_id:
            return Response({'message': 'Litre id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Litre.objects.filter(id=litre_id).exists():
            litre = Litre.objects.get(id=litre_id)
            litre.delete()
            return Response({'message': 'success'}, status=status.HTTP_200_OK)
        return Response({'message': 'Litre does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response({'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)
