from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from attribute.models import Planter, PlanterSize
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission
from rest_framework import serializers

class PlanterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planter
        fields = '__all__'

# get planters by planter size
@api_view(['GET'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def get_planters_by_planter_size(request, pk):
    if request.method == 'GET' and pk:
        required_permissions = [
            'attribute.view_plantersize'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if not PlanterSize.objects.filter(id=pk).exists():
            return Response(data={'message': 'Planter Size does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
        
        planter_size = PlanterSize.objects.get(id=pk)
        planters = Planter.objects.filter(planter_size=planter_size)
        serializer = PlanterSerializer(planters, many=True)
        data = {
            'planters': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)