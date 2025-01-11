from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from product.models import Product, MainProductImage
from django.conf import settings
from rest_framework import serializers
from attribute.models import Size
from attribute.models import PlanterSize
from attribute.models import Planter
from attribute.models import Color

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'color_name', 'color_code']

class PlanterSerializer(serializers.ModelSerializer):
    class Meta:
        model = Planter
        fields = ['id', 'name']
        
class PlanterSizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanterSize
        fields = ['id', 'name', 'size']

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name', 'size']

class ProductSerializer(serializers.ModelSerializer):
    # Include main product image as the first element in the images list
    images = serializers.SerializerMethodField()
    # add short_description from MainProduct
    short_description = serializers.ReadOnlyField(source='product_id.short_description')
    main_product_name = serializers.ReadOnlyField(source='product_id.name')

    class Meta:
        model = Product
        fields = ['id', 'price', 'images', 'short_description', 'main_product_name', 'size_id', 'planter_size_id', 'planter_id', 'color_id']

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
def filter_product(request, pk):
    if request.method == 'GET' and pk:
        
        if Product.objects.filter(id=pk).exists():

            # Initialize an empty filter dictionary
            filter_params = {}

            # Extract query parameters from the request
            size_id = request.query_params.get('size_id', None)
            planter_size_id = request.query_params.get('planter_size_id', None)
            planter_id = request.query_params.get('planter_id', None)
            color_id = request.query_params.get('color_id', None)

            # Only add to the filter dictionary if the parameter is provided
            current_product = Product.objects.filter(id=pk).first()
            product_id = current_product.product_id
            filter_params = {'product_id': product_id}
            if size_id:
                filter_params['size_id'] = size_id
            if planter_size_id:
                filter_params['planter_size_id'] = planter_size_id
            if planter_id:
                filter_params['planter_id'] = planter_id
            if color_id:
                filter_params['color_id'] = color_id

            # Query the products based on the filters
            product = Product.objects.filter(**filter_params).first()
            
            serializer = ProductSerializer(product, context={'request': request})
            
            # return all unique size_id of the product
            product_size_ids = Product.objects.filter(product_id=product_id).values_list('size_id', flat=True).distinct()
            product_planter_size_ids = Product.objects.filter(product_id=product_id).values_list('planter_size_id', flat=True).distinct()
            product_planter_ids = Product.objects.filter(product_id=product_id).values_list('planter_id', flat=True).distinct()
            product_color_ids = Product.objects.filter(product_id=product_id).values_list('color_id', flat=True).distinct()

            product_sizes = SizeSerializer(Size.objects.filter(id__in=product_size_ids), many=True)
            product_planter_sizes = PlanterSizeSerializer(PlanterSize.objects.filter(id__in=product_planter_size_ids), many=True)
            product_planter = PlanterSerializer(Planter.objects.filter(id__in=product_planter_ids), many=True)
            product_color = ColorSerializer(Color.objects.filter(id__in=product_color_ids), many=True)
            

            data = {
                'product': serializer.data,
                'product_sizes': product_sizes.data,
                'product_planter_sizes': product_planter_sizes.data,
                'product_planters': product_planter.data,
                'product_colors': product_color.data
            }
            return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)