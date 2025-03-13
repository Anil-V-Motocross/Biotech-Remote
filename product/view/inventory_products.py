from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from product.models import Product
from product.serializers import ProductInventorySerializer
from account.permissions import DynamicPermission


@api_view(['GET'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def list_products(request):
    """
    API to list all products with optional filtering by name, type, and SKU.
    Supports pagination.
    """
    if not request.user.is_staff:
        return Response(
            {'message': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN
        )    
    required_permissions = ['product.view_product']

    if not any(request.user.has_perm(perm) for perm in required_permissions):
        return Response(
            {'message': 'You do not have permission to perform this action.'},
            status=status.HTTP_403_FORBIDDEN
        )

    query_name = request.query_params.get('name', None)
    query_type = request.query_params.get('type', None)  # Filter by MainProduct type
    query_sku = request.query_params.get('sku', None)

    products = Product.objects.all()

    # Apply filters
    if query_name:
        products = products.filter(name__icontains=query_name)

    if query_type:
        products = products.filter(product_id__type=query_type)  

    if query_sku:
        products = products.filter(sku__icontains=query_sku)

    # Pagination
    paginator = PageNumberPagination()
    paginator.page_size = 10  # Adjust as needed
    paginated_products = paginator.paginate_queryset(products, request)

    serializer = ProductInventorySerializer(paginated_products, many=True)
    return paginator.get_paginated_response(serializer.data)
