from rest_framework.decorators import api_view,permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from product.models import MainProduct
from product.serializers import MainProductMinimalSerializer
from account.permissions import DynamicPermission

@api_view(['GET'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def admin_search_products(request):
    required_permissions = ['product.view_product']
    
    if not any(request.user.has_perm(perm) for perm in required_permissions):
        return Response(
            {'message': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN
        )     

    query_type = request.query_params.get('type', None)
    query_name = request.query_params.get('name', None)

    if query_type:
        products = MainProduct.objects.filter(type=query_type).only('id', 'name')

    elif query_name:
        products = MainProduct.objects.filter(name__icontains=query_name).only('id', 'name')

    else:
        return Response({'message': 'Provide a valid search query.'}, status=status.HTTP_400_BAD_REQUEST)

    serializer = MainProductMinimalSerializer(products, many=True)
    return Response({'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)