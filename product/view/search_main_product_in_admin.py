from rest_framework.decorators import api_view,permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.response import Response
from rest_framework import status
from product.models import MainProduct, Product
from product.serializers import MainProductMinimalSerializer, ProductMinimalSerializer
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

    query_type = request.query_params.get('type', None)  # Search based on MainProduct type
    query_name = request.query_params.get('name', None)  # Search based on name
    search_in = request.query_params.get('search_in', 'main')  # Default to searching in MainProduct

    if search_in == 'main':
        # Searching in MainProduct
        if query_type and query_name:
            products = MainProduct.objects.filter(type=query_type, name__icontains=query_name).only('id', 'name')
        elif query_type:
            products = MainProduct.objects.filter(type=query_type).only('id', 'name')
        elif query_name:
            products = MainProduct.objects.filter(name__icontains=query_name).only('id', 'name')
        else:
            return Response({'message': 'Provide a valid search query.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = MainProductMinimalSerializer(products, many=True)

    elif search_in == 'product':
        # Searching in Product, but using the type from MainProduct
        if query_type and query_name:
            products = Product.objects.filter(
                product_id__type=query_type, name__icontains=query_name
            ).only('id', 'name', 'sku')
        elif query_type:
            products = Product.objects.filter(product_id__type=query_type).only('id', 'name', 'sku')
        elif query_name:
            products = Product.objects.filter(name__icontains=query_name).only('id', 'name', 'sku')
        else:
            return Response({'message': 'Provide a valid search query for products.'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProductMinimalSerializer(products, many=True)

    else:
        return Response({'message': 'Invalid search type. Use search_in=main or search_in=product.'}, status=status.HTTP_400_BAD_REQUEST)

    return Response({'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
