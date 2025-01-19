from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from order.models import Wishlist
from account.permissions import DynamicPermission
from rest_framework import serializers
from product.models import Product

class WishlistSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='product_id.product_id.name', read_only=True)
    image = serializers.CharField(source='product_id.image.url', read_only=True)  # Assuming product has the image field
    price = serializers.CharField(source='product_id.price', read_only=True)  # Price from the Product model
    stock_status = serializers.SerializerMethodField()  # Adding a custom field for stock status

    class Meta:
        model = Wishlist
        fields = ['id', 'user_id', 'product_id', 'name', 'image', 'price', 'stock_status']

    def get_stock_status(self, instance):
        # Access the Product associated with the Cart item
        product = instance.product_id

        # Get the stock quantity from the Product model
        stock_quantity = int(product.stock)  # Ensure stock is treated as an integer
        
        # Return "Out Of Stock" if stock is 0, else "In Stock"
        if stock_quantity == 0:
            return "Out Of Stock"
        else:
            return "In Stock"
        

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def wishlist(request):
    if request.method == 'GET':
        required_permissions = [
            'order.view_wishlist'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        main_product_id= request.query_params.get('main_prod_id', None)
        product_id = request.query_params.get('prod_id', None)
        
        if main_product_id or product_id:
            if main_product_id:
                product_id = Product.objects.filter(product_id=main_product_id, is_default=True).first()
                product_id = product_id.id
                if Wishlist.objects.filter(user_id=request.user.id, product_id=product_id).exists():
                    data = {
                        "in_wishlist": True
                    }
                    return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
                else:
                    data = {
                        "in_wishlist": False
                    }
                    return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
            else:
                if Wishlist.objects.filter(user_id=request.user.id, product_id=product_id).exists():
                    data = {
                        "in_wishlist": True
                    }
                    return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
                else:
                    data = {
                        "in_wishlist": False
                    }
                    return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
        
        wishlists = Wishlist.objects.filter(user_id=request.user.id).all()
        serializer = WishlistSerializer(wishlists, many=True)
        data = {
            'wishlists': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        required_permissions = [
            'order.add_wishlist'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        main_product_id = request.data.get('main_prod_id', None)
        
        if main_product_id:
            product_id = Product.objects.filter(product_id=main_product_id, is_default=True).first()
            product_id = product_id.id
        else:
            product_id = request.data.get('prod_id')
            
        # Check if the product is already in the wishlist for the user
        # if exists then delete
        if Wishlist.objects.filter(user_id=request.user.id, product_id=product_id).exists():
            wishlist = Wishlist.objects.get(user_id=request.user.id, product_id=product_id)
            wishlist.delete()
            return Response(data={'message': 'Product removed from wishlist'}, status=status.HTTP_200_OK)
        else:
            # If the product is not in the wishlist, add it
            data = {
                'user_id': request.user.id,
                'product_id': product_id
            }
            serializer = WishlistSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return Response(data={'message': 'Product added to wishlist'}, status=status.HTTP_200_OK)
            else:
                return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    # if request.method == 'DELETE' and pk:
    #     required_permissions = [
    #         'order.delete_wishlist'
    #     ]
        
    #     if not any(request.user.has_perm(perm) for perm in required_permissions):
    #         return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
    #     if Wishlist.objects.filter(id=pk, user_id=request.user.id).exists():
    #         wishlist = Wishlist.objects.get(id=pk, user_id=request.user.id)
    #         wishlist.delete()
    #         return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
    #     return Response(data={'message': 'Wishlist does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    