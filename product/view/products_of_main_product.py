from rest_framework.response import Response
from rest_framework import status
from product.models import Product
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission
from rest_framework import serializers

class ProductSerializer(serializers.ModelSerializer):
    main_product_name = serializers.CharField(source='product_id.name', read_only=True)
    size = serializers.CharField(source='size_id.name', read_only=True)
    planter_size = serializers.CharField(source='planter_size_id.name', read_only=True)
    planter = serializers.CharField(source='planter_id.name', read_only=True)
    color = serializers.CharField(source='color_id.color_code', read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 
            'main_product_name',  # Instead of size_id, this gives the name of MainProduct
            'size',               # Custom field for size name
            'planter_size',
            'planter',
            'color',
            'weight_id',
            'name',
            'price',
            'discount',
            'stock',
            'sku',
            'image',
            'visible_online',
            'date_added',
            'is_default'
        ]

    def get_size(self, obj):
        # Get the name from the Size model if size_id is not null
        if obj.size_id:
            return obj.size_id.name
        return None

@api_view(['GET'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def products_of_main_product(request, pk=None):
    if request.method == 'GET' and pk:
        required_permissions = [
            'product.view_product'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        products = Product.objects.filter(product_id=pk).all()
        
        serializer = ProductSerializer(products, many=True)
        data = {
            'products': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
        
        