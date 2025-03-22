from rest_framework.decorators import api_view
from rest_framework.response import Response
from product.models import MainProduct, MainProductImage
from rest_framework import status
from rest_framework import serializers

from rest_framework import serializers

class MainProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainProductImage
        fields = ['id', 'image']
    

# Serializer for MainProduct, with related images
class MainProductSerializer(serializers.ModelSerializer):
    images = MainProductImageSerializer(many=True, read_only=True)  # Include related images

    class Meta:
        model = MainProduct
        fields = ['id', 'name', 'default_mrp', 'default_selling_price', 'default_discount_amount', 'default_sku', 'is_featured', 'is_best_seller', 'is_seasonal_collection', 'is_trending', 'images']

    def to_representation(self, instance):
        # Call the parent class to get the default representation
        representation = super().to_representation(instance)

        # Get the first image from the images list, if any
        if representation['images']:
            representation['image'] = representation['images'][0]['image']
        else:
            representation['image'] = None  # If no images, set image to None

        # Optionally, remove the 'images' field if you don't need it in the response
        representation.pop('images', None)

        return representation

@api_view(['GET'])
def sort_by(request):
    if request.method == 'GET':
        sort_by = request.query_params.get('sort_by', None)

        # Check if 'sort_by' is 'a-z' and sort alphabetically A-Z
        if sort_by == 'a-z':
            products = MainProduct.objects.all().order_by('name')  # Sort alphabetically A-Z
        # Check if 'sort_by' is 'z-a' and sort alphabetically Z-A
        elif sort_by == 'z-a':
            products = MainProduct.objects.all().order_by('-name')  # Sort alphabetically Z-A
        else:
            # Handle other sorting logic here or default to unsorted if not recognized
            products = MainProduct.objects.all()

        serializer = MainProductSerializer(products, many=True)
        
        data = {
            'products': serializer.data
        }

        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)

    return Response(data={'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)
