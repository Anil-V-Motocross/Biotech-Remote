from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from product.models import MainProduct, ProductSubCategory, MainProductImage

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
def subcategory_products(request, subcategory_id=None):
    if subcategory_id is None:
        return Response({"detail": "Subcategory ID is required."}, status=status.HTTP_400_BAD_REQUEST)

    # Query ProductSubCategory to get all products related to the subcategory_id
    products_in_subcategory = ProductSubCategory.objects.filter(subcategory_id=subcategory_id)

    if not products_in_subcategory.exists():
        return Response({"detail": "No products found for this subcategory."}, status=status.HTTP_404_NOT_FOUND)

    # Extract the product_ids from the ProductSubCategory
    product_ids = products_in_subcategory.values_list('product_id', flat=True)

    # Fetch the MainProduct objects related to the product_ids
    products = MainProduct.objects.filter(id__in=product_ids)

    # Serialize the products using the MainProductSerializer
    serializer = MainProductSerializer(products, many=True)

    # Return the serialized data
    return Response(serializer.data)
