from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from product.models import ProductCategory, ProductSubCategory, ProductTag
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission  
from category.models import Category, SubCategory
from product.models import MainProduct

        

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
        
        # {'tags': ['positivity', 'fresh air'], 'category': [7, 10], 'product_id': 13}

        product_id = request.data.get('product_id')
        tags = request.data.get('tags')
        subcategory = request.data.get('category')

        if product_id and tags and subcategory:
            product_id = MainProduct.objects.get(id=product_id)
            # Save the tags
            for tag in tags:
                ProductTag.objects.create(product_id=product_id, tag=tag)

            # Save the category
            for subcat in subcategory:
                subcat = SubCategory.objects.get(id=subcat)
                cat  = Category.objects.get(id=subcat.category_id)
                ProductCategory.objects.create(product_id=product_id, category_id=cat)

                # Add ProductSubCategory
                ProductSubCategory.objects.create(product_id=product_id, subcategory_id=subcat)

        return Response(data={"message": "success"}, status=status.HTTP_201_CREATED)
    
    return Response(data={'message': 'Something went wrong.'}, status=status.HTTP_400_BAD_REQUEST)