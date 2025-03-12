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
    mrp = serializers.FloatField(source='product_id.sale_price',read_only=True)
    class Meta:
        model = Wishlist
        fields = ['id', 'user_id', 'product_id', 'name', 'image', 'price', 'mrp', 'stock_status']

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
def wishlist(request, pk=None):
    if request.method == 'GET' and not pk:
        required_permissions = [
            'order.view_wishlist'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        product_id = request.query_params.get('prod_id', None)
        main_product_id_list = request.query_params.getlist('main_product_id_list', None)
        
        if main_product_id_list and not product_id:
            wishlist_items = Wishlist.objects.filter(
                                                    user_id=request.user,
                                                    product_id__is_default=True
                                                    ).select_related('product_id__product_id')
        
            main_product_ids = list(wishlist_items.values_list('product_id__product_id', flat=True).distinct())
            
            return Response(data={'main_product_ids': main_product_ids},status=status.HTTP_200_OK)
            
        if product_id and not main_product_id_list:
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
    
    if request.method == 'POST' and not pk:
        required_permissions = [
            'order.add_wishlist', 'order.delete_wishlist'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        main_product_id = request.data.get('main_prod_id', None)
        print('wishlist main id-----:', main_product_id)

        if main_product_id:
            product_id = Product.objects.filter(product_id=main_product_id, is_default=True).first()
            product_id = product_id.id
        else:
            product_id = request.data.get('prod_id')
            print('wishlist produ id ----:', product_id)
        
        # Check if the product is already in the wishlist for the user
        # if exists then delete
        if Wishlist.objects.filter(user_id=request.user.id, product_id=product_id).exists():
            wishlist = Wishlist.objects.get(user_id=request.user.id, product_id=product_id)
            wishlist.delete()
            data = {
                "in_wishlist": False
            }
            return Response(data={'message': 'Product removed from wishlist', 'data': data}, status=status.HTTP_200_OK)
        else:
            # If the product is not in the wishlist, add it
            data = {
                'user_id': request.user.id,
                'product_id': product_id
            }
            serializer = WishlistSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                data = {
                    "in_wishlist": True
                }
                return Response(data={'message': 'Product added to wishlist', 'data': data}, status=status.HTTP_200_OK)
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

    if request.method == 'DELETE':
        required_permissions = ['order.delete_wishlist']

        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        # Case 1: Delete by Wishlist ID (Existing Logic)
        if pk:
            if Wishlist.objects.filter(id=pk, user_id=request.user.id).exists():
                wishlist = Wishlist.objects.get(id=pk, user_id=request.user.id)
                wishlist.delete()
                return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
            return Response(data={'message': 'Wishlist does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

        # Case 2: Delete by Main Product ID (New Logic)
        main_product_id = request.GET.get('main_product_id')

        if main_product_id:
            main_product_id = main_product_id.rstrip('/')  # Fix trailing slash issue

            try:
                main_product_id = int(main_product_id)  # Ensure it's an integer
            except ValueError:
                return Response({'message': 'Invalid main_product_id. Must be an integer.'}, status=status.HTTP_400_BAD_REQUEST)

            # Find the default product linked to this main product
            default_product = Product.objects.filter(product_id_id=main_product_id, is_default=True).first()

            if default_product:
                # Check if the default product exists in the user's wishlist
                wishlist_item = Wishlist.objects.filter(product_id=default_product, user_id=request.user.id).first()

                if wishlist_item:
                    wishlist_item.delete()
                    return Response(data={'message': 'Default product removed from wishlist.'}, status=status.HTTP_200_OK)
                return Response(data={'message': 'Default product not found in wishlist.'}, status=status.HTTP_400_BAD_REQUEST)

            return Response(data={'message': 'No default product found for this Main Product.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={'message': 'Invalid request parameters.'}, status=status.HTTP_400_BAD_REQUEST)
    