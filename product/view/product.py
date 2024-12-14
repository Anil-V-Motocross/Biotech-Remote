from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from product.models import MainProduct, MainProductImage
from rest_framework import status
from rest_framework.response import Response
from rest_framework import serializers

class MainProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainProduct
        fields = '__all__'

class MainProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainProductImage
        fields = '__all__'



@api_view(['POST'])
def product(request):
    if request.method == 'POST':
        parser_classes = [MultiPartParser, FormParser]

        print("Received request to add product with images.")

        # Extract product data
        product_data = {
            'name': request.data.get('name'),
            'short_description': request.data.get('short_description'),
            'ribbon': request.data.get('ribbon'),
            'threshold': request.data.get('threshold'),
            'description': request.data.get('description'),
            'whats_included': request.data.get('whats_included'),
            'vedio_link': request.data.get('vedio_link')
        }

        print("Extracted product data:", product_data)

        # Serialize and save product
        product_serializer = MainProductSerializer(data=product_data)
        if product_serializer.is_valid():
            product = product_serializer.save()
            print("Product saved successfully with ID:", product.id)
        else:
            print("Product serialization failed with errors:", product_serializer.errors)
            return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Handle images
        images = request.FILES.getlist('images')
        print("Number of images received:", len(images))

        image_instances = []
        for idx, image in enumerate(images):
            print(f"Processing image {idx + 1}:", image.name)
            image_data = {
                'product': product.id,
                'image': image
            }
            image_serializer = MainProductImageSerializer(data=image_data)
            if image_serializer.is_valid():
                saved_image = image_serializer.save()
                image_instances.append(saved_image)
                print(f"Image {idx + 1} saved successfully with ID:", saved_image.id)
            else:
                print(f"Image {idx + 1} serialization failed with errors:", image_serializer.errors)
                return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        print("All images processed successfully.")

        return Response({
            'product': product_serializer.data,
            'images': [MainProductImageSerializer(instance).data for instance in image_instances]
        }, status=status.HTTP_201_CREATED)
