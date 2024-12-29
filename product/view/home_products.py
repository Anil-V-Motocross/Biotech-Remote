from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from product.models import MainProduct, MainProductImage
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
        fields = ['id', 'name', 'is_featured', 'is_best_seller', 'is_seasonal_collection', 'is_trending', 'images']

    def to_representation(self, instance):
        # Call the parent class to get the default representation
        representation = super().to_representation(instance)

        # Get the first image from the images list, if any
        if representation['images']:
            representation['image'] = representation['images'][0]['image']
        else:
            representation['image'] = None  # If no images, set image to None

        # Add a dummy 'price' field
        representation['price'] = '500'

        # Optionally, remove the 'images' field if you don't need it in the response
        representation.pop('images', None)

        return representation


@api_view(['GET'])
def home_products(request):
    if request.method == 'GET':

        products = MainProduct.objects.all()

        serializer = MainProductSerializer(products, many=True)

        data = {
            'products': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)

    return Response(data={'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)