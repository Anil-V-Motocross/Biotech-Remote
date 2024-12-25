from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from product.models import Product
from rest_framework import serializers
from product.models import Product

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

@api_view(['GET'])
def default_product(request, product_id=None):
    if request.method == 'GET':
        # Filter the product to get the default one with the specified product_id
        product = Product.objects.filter(product_id=product_id, is_default=True).first()
        
        # Check if the product exists
        if product is None:
            return Response(data={'message': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the single product (do not use `many=True`)
        serializer = ProductSerializer(product)
        
        # Prepare the response data
        data = {
            'product': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)

    return Response(data={'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)
