from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from product.models import Product
from rest_framework import serializers
from product.models import Product, MainProductImage
from django.conf import settings

class ProductSerializer(serializers.ModelSerializer):
    # Include main product image as the first element in the images list
    images = serializers.SerializerMethodField()
    # add short_description from MainProduct
    short_description = serializers.ReadOnlyField(source='product_id.short_description')
    main_product_name = serializers.ReadOnlyField(source='product_id.name')

    class Meta:
        model = Product
        fields = ['id', 'name', 'price', 'is_default', 'images', 'short_description', 'main_product_name']

    def get_images(self, obj):
        # Start with the product's main image
        image_list = [{"image": self.get_absolute_url(obj.image)}] if obj.image else []
        
        # Add the related MainProductImages
        main_product_images = MainProductImage.objects.filter(product=obj.product_id)
        for main_product_image in main_product_images:
            image_list.append({"image": self.get_absolute_url(main_product_image.image)})

        return image_list

    def get_absolute_url(self, image_field):
        """
        This method constructs the absolute URL for the given image field.
        It uses request.build_absolute_uri() with MEDIA_URL to construct the full URL.
        """
        request = self.context.get('request')  # Get the request object from the context
        if request and image_field:
            # Generate the full absolute URL for the image
            return request.build_absolute_uri(settings.MEDIA_URL + image_field.name)
        return None 


@api_view(['GET'])
def default_product(request, product_id=None):
    if request.method == 'GET':
        # Filter the product to get the default one with the specified product_id
        product = Product.objects.filter(product_id=product_id, is_default=True).first()
        
        # Check if the product exists
        if product is None:
            return Response(data={'message': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the single product (do not use `many=True`)
        serializer = ProductSerializer(product, context={'request': request})
        
        # Prepare the response data
        data = {
            'product': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)

    return Response(data={'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)
