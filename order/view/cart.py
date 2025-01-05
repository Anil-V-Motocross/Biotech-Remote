from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from order.models import Cart
from product.models import Product, MainProduct
from rest_framework import serializers
from account.permissions import DynamicPermission


class CartSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='product_id.product_id.name', read_only=True)
    image = serializers.CharField(source='product_id.image.url', read_only=True)  # Assuming product has the image field
    price = serializers.CharField(source='product_id.price', read_only=True)  # Price from the Product model
    short_description = serializers.CharField(source='product_id.product_id.short_description', read_only=True)
    stock_status = serializers.SerializerMethodField()  # Adding a custom field for stock status

    class Meta:
        model = Cart
        fields = ['id', 'user_id', 'product_id','quantity', 'name', 'image', 'price', 'short_description', 'stock_status']

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




@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def cart(request, pk=None):
    if request.method == 'GET' and not pk:
        required_permissions = [
            'order.view_cart'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        cart = Cart.objects.filter(user_id=request.user.id).all()
        serializer = CartSerializer(cart, many=True)
        data = {
            'cart': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        required_permissions = [
            'order.add_cart'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        product_id = request.data.get('prod_id')
        data = {
            'user_id': request.user.id,
            'product_id': product_id,
            'quantity': request.data.get('quantity')
            }
        serializer = CartSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'success'}, status=status.HTTP_201_CREATED)
        if serializer.errors:
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
    if request.method == 'PATCH':
        required_permissions = [
            'order.change_cart'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        cart_id = request.data.get('cart_id')
        
        if not cart_id:
            return Response(data={'message': 'Cart id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Cart.objects.filter(id=cart_id).exists():
            cart = Cart.objects.get(id=cart_id)
            serializer = CartSerializer(instance=cart, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
            if serializer.errors:
                return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': 'Cart does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'DELETE' and pk:
        required_permissions = [
            'order.delete_cart'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if Cart.objects.filter(id=pk, user_id=request.user.id).exists():
            cart = Cart.objects.get(id=pk, user_id=request.user.id)
            cart.delete()
            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Cart does not exist.'}, status=status.HTTP_400_BAD_REQUEST)