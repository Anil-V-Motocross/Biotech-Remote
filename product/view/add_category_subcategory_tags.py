from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from product.models import ProductCategory, ProductSubCategory, ProductTag
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission  
from rest_framework import serializers 


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['product_id', 'category_id']

class ProductSubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSubCategory
        fields = ['product_id', 'subcategory_id']


class ProductTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductTag
        fields = ['product_id', 'tag']
        

@api_view(['POST'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def add_category_subcategory_tags(request):
    if request.method == 'POST':
        required_permissions = [
            'product.add_productcategory', 'product.add_productsubcategory', 'product.add_producttag'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        

        return Response(data={"message": "success"}, status=status.HTTP_201_CREATED)
    
    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)