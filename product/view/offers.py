from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.pagination import PageNumberPagination
from product.models import Product
from product.serializers import ProductSerializer 
from account.token_permissions import OptionalTokenAuthentication  

@api_view(['GET'])
@permission_classes([AllowAny])
@authentication_classes([OptionalTokenAuthentication])
def list_discounted_products(request):
    try:
        # Filter products
        products = Product.objects.filter(discount__gt=25, visible_online=True)

        # Paginate results
        paginator = PageNumberPagination()
        paginated_products = paginator.paginate_queryset(products, request)

        # Serialize
        serializer = ProductSerializer(paginated_products, many=True, context={'request': request})

        return Response({
            "message": "success",
            "products": serializer.data,
            "count": paginator.page.paginator.count,
            "next": paginator.get_next_link(),
            "previous": paginator.get_previous_link()
        }, status=200)

    except Exception as e:
        return Response({
            "message": "An error occurred",
            "error": str(e)
        }, status=500)
