from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from product.models import Product, MainProduct
from account.permissions import DynamicPermission


@api_view(['PATCH'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def update_default_product(request, product_id):
    if request.method == 'PATCH':
        required_permissions = [
            'product.edit_product'
        ]
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)     
        
        try:
            selected_product = Product.objects.get(id=product_id)
            main_product = selected_product.product_id
            
            # Setting the selected product as default
            Product.objects.filter(product_id=main_product).update(is_default=False)
            selected_product.is_default = True
            selected_product.save()
            
            # Updating main product default fields
            main_product.default_sale_price = selected_product.price
            main_product.default_price = selected_product.price
            main_product.default_discount = selected_product.discount
            main_product.default_sku = selected_product.sku
            main_product.save()
            
            return Response({'message': 'Default product updated successfully.'}, status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'message': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    return Response(data={'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)