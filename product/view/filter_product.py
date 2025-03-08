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
from attribute.models import Weight
from attribute.models import Material, Shape, PotType, Litre
from rest_framework.exceptions import ValidationError
from order.models import Cart, Wishlist

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

class WeightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weight
        fields = ['id', 'size_grams']

class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name']

class ShapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shape
        fields = ['id', 'name']

class PotTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PotType
        fields = ['id', 'name']   

class LitreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Litre
        fields = ['id', 'name']


class ProductSerializer(serializers.ModelSerializer):
    # Include main product image as the first element in the images list
    images = serializers.SerializerMethodField()
    # add short_description from MainProduct
    short_description = serializers.ReadOnlyField(source='product_id.short_description')
    main_product_name = serializers.ReadOnlyField(source='product_id.name')
    is_cart = serializers.SerializerMethodField()
    is_wishlist = serializers.SerializerMethodField()


    class Meta:
        model = Product
        fields = ['id', 'price', 'is_cart', 'is_wishlist', 'images', 'short_description', 'main_product_name', 'size_id', 'planter_size_id', 'planter_id', 'weight_id', 'litre_id', 'color_id']

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

    def get_is_cart(self, obj):
        """Check if the product exists in the user's cart."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return Cart.objects.filter(user_id=user, product_id=obj).exists()
        return False

    def get_is_wishlist(self, obj):
        """Check if the product exists in the user's wishlist."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return Wishlist.objects.filter(user_id=user, product_id=obj).exists()
        return False

@api_view(['GET'])
def filter_product(request, pk):
    if request.method == 'GET' and pk:
        
        if Product.objects.filter(id=pk).exists():

            # Initialize an empty filter dictionary
            # filter_params = {}

            current_product = Product.objects.filter(id=pk).first()
            print('current product ----:', current_product)
            if not current_product:
                print('exit from initial get')
                return Response({'message': 'Product not found'}, status=status.HTTP_400_BAD_REQUEST)
            product_id = current_product.product_id
            product_type = product_id.type
            print("-------------product_type:", product_type)
            print("-------------product_id:", product_id)

            print('--------------------------------------------------------------------')

            if product_type == 'seed':
                filter_params = {}
                current_product = Product.objects.filter(id=pk).first()
                product_id = current_product.product_id
                filter_params = {'product_id': product_id, 'visible_online': True}
                
                weight_id = request.query_params.get('weight_id', None)
                print('seed-----------------',weight_id)
                if len(request.query_params) > 1: 
                    raise ValidationError("Only 'weight_id' can be used for seed products.")
                
                filter_params = {'product_id': product_id, 'visible_online': True}

                if weight_id:
                    filter_params['weight_id'] = weight_id

                product = Product.objects.filter(**filter_params).first()
                if not product:
                    return Response({'message': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

                # Available weight options for the seed product
                product_weight_ids = Product.objects.filter(product_id=product_id, visible_online=True).values_list('weight_id', flat=True).distinct()
                product_weights = WeightSerializer(Weight.objects.filter(id__in=product_weight_ids), many=True) if product_weight_ids else None

                serializer = ProductSerializer(product, context={'request': request})
                data = {
                    'product_type': product_type,
                    'product': serializer.data,
                    'product_weights': product_weights.data,
                }
                return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)

            elif product_type == 'plant':
                filter_params = {}

                # Extract query parameters from the request
                size_id = request.query_params.get('size_id', None)
                planter_size_id = request.query_params.get('planter_size_id', None)
                planter_id = request.query_params.get('planter_id', None)
                color_id = request.query_params.get('color_id', None)
                print('plant-----------------',size_id,planter_size_id,planter_id,color_id)

                # Only add to the filter dictionary if the parameter is provided
                # product_id = current_product.product_id
                # filter_params = {'product_id': product_id, 'visible_online': True}
                current_product = Product.objects.filter(id=pk).first()
                product_id = current_product.product_id
                filter_params = {'product_id': product_id, 'visible_online': True}
                print(":-------:",product_id, filter_params)
                if size_id and not planter_size_id and not planter_id and not color_id:
                    filter_params['size_id'] = size_id
                    
                    product = Product.objects.filter(**filter_params).first()
                    print("-------prod:", product)
                    
                    if not product:
                        return Response(data={'message': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
                
                    product_size_ids = Product.objects.filter(product_id=product_id, visible_online=True).values_list('size_id', flat=True).distinct()
                    product_planter_size_ids = Product.objects.filter(product_id=product_id, size_id=product.size_id, visible_online=True).values_list('planter_size_id', flat=True).distinct()
                    filter_params['planter_size_id'] = product_planter_size_ids[0]
                    product_planter_ids = Product.objects.filter(**filter_params).values_list('planter_id', flat=True).distinct()
                    filter_params['planter_id'] = product_planter_ids[0]
                    product_color_ids = Product.objects.filter(**filter_params).values_list('color_id', flat=True).distinct()
                    filter_params['color_id'] = product_color_ids[0]
                    
                    product_sizes = SizeSerializer(Size.objects.filter(id__in=product_size_ids), many=True)
                    product_planter_sizes = PlanterSizeSerializer(PlanterSize.objects.filter(id__in=product_planter_size_ids), many=True)
                    product_planter = PlanterSerializer(Planter.objects.filter(id__in=product_planter_ids), many=True)
                    product_color = ColorSerializer(Color.objects.filter(id__in=product_color_ids), many=True)
            

                    product_sizes = SizeSerializer(Size.objects.filter(id__in=product_size_ids), many=True)
                    product_planter_sizes = PlanterSizeSerializer(PlanterSize.objects.filter(id__in=product_planter_size_ids), many=True)
                    product_planter = PlanterSerializer(Planter.objects.filter(id__in=product_planter_ids), many=True)
                    product_color = ColorSerializer(Color.objects.filter(id__in=product_color_ids), many=True)
                    
                elif size_id and planter_size_id and not planter_id and not color_id:
                    filter_params['size_id'] = size_id
                    filter_params['planter_size_id'] = planter_size_id
                    product = Product.objects.filter(**filter_params).first()
                    
                    if not product:
                        return Response(data={'message': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
                
                    product_size_ids = Product.objects.filter(product_id=product_id, visible_online=True).values_list('size_id', flat=True).distinct()
                    product_planter_size_ids = Product.objects.filter(product_id=product_id, size_id=product.size_id, visible_online=True).values_list('planter_size_id', flat=True).distinct()
                    product_planter_ids = Product.objects.filter(**filter_params).values_list('planter_id', flat=True).distinct()
                    filter_params['planter_id'] = product_planter_ids[0]
                    product_color_ids = Product.objects.filter(**filter_params).values_list('color_id', flat=True).distinct()
                    filter_params['color_id'] = product_color_ids[0]
                    
                    product_sizes = SizeSerializer(Size.objects.filter(id__in=product_size_ids), many=True)
                    product_planter_sizes = PlanterSizeSerializer(PlanterSize.objects.filter(id__in=product_planter_size_ids), many=True)
                    product_planter = PlanterSerializer(Planter.objects.filter(id__in=product_planter_ids), many=True)
                    product_color = ColorSerializer(Color.objects.filter(id__in=product_color_ids), many=True)
                    
                elif size_id and planter_size_id and planter_id and not color_id:
                    filter_params['size_id'] = size_id
                    filter_params['planter_size_id'] = planter_size_id
                    filter_params['planter_id'] = planter_id
                    product = Product.objects.filter(**filter_params).first()
                    
                    if not product:
                        return Response(data={'message': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
                
                    product_size_ids = Product.objects.filter(product_id=product_id, visible_online=True).values_list('size_id', flat=True).distinct()
                    product_planter_size_ids = Product.objects.filter(product_id=product_id, size_id=product.size_id, visible_online=True).values_list('planter_size_id', flat=True).distinct()
                    product_planter_ids = Product.objects.filter(product_id=product_id, size_id=product.size_id, planter_size_id=product.planter_size_id, visible_online=True).values_list('planter_id', flat=True).distinct()
                    product_color_ids = Product.objects.filter(**filter_params).values_list('color_id', flat=True).distinct()
                    filter_params['color_id'] = product_color_ids[0]
                    
                    product_sizes = SizeSerializer(Size.objects.filter(id__in=product_size_ids), many=True)
                    product_planter_sizes = PlanterSizeSerializer(PlanterSize.objects.filter(id__in=product_planter_size_ids), many=True)
                    product_planter = PlanterSerializer(Planter.objects.filter(id__in=product_planter_ids), many=True)
                    product_color = ColorSerializer(Color.objects.filter(id__in=product_color_ids), many=True)
                    
                elif size_id and planter_size_id and planter_id and color_id:
                    filter_params['size_id'] = size_id
                    filter_params['planter_size_id'] = planter_size_id
                    filter_params['planter_id'] = planter_id
                    filter_params['color_id'] = color_id
                    product = Product.objects.filter(**filter_params).first()
                    
                    if not product:
                        return Response(data={'message': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    product_size_ids = Product.objects.filter(product_id=product_id, visible_online=True).values_list('size_id', flat=True).distinct()
                    product_planter_size_ids = Product.objects.filter(product_id=product_id, size_id=product.size_id, visible_online=True).values_list('planter_size_id', flat=True).distinct()
                    product_planter_ids = Product.objects.filter(product_id=product_id, size_id=product.size_id, planter_size_id=product.planter_size_id, visible_online=True).values_list('planter_id', flat=True).distinct()
                    product_color_ids = Product.objects.filter(product_id=product_id, size_id=product.size_id, planter_size_id=product.planter_size_id, planter_id=product.planter_id, visible_online=True).values_list('color_id', flat=True).distinct()
                    
                    product_sizes = SizeSerializer(Size.objects.filter(id__in=product_size_ids), many=True)
                    product_planter_sizes = PlanterSizeSerializer(PlanterSize.objects.filter(id__in=product_planter_size_ids), many=True)
                    product_planter = PlanterSerializer(Planter.objects.filter(id__in=product_planter_ids), many=True)
                    product_color = ColorSerializer(Color.objects.filter(id__in=product_color_ids), many=True)
                else:
                    return Response(data={'message': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
                
                product = Product.objects.filter(**filter_params).first()
                serializer = ProductSerializer(product, context={'request': request})
                data = {
                    'product_type': product_type,
                    'product': serializer.data,
                    'product_sizes': product_sizes.data,
                    'product_planter_sizes': product_planter_sizes.data,
                    'product_planters': product_planter.data,
                    'product_colors': product_color.data,
                }
                return Response(data={'message': 'success111', 'data': data}, status=status.HTTP_200_OK)
            
            elif product_type == 'pot':
                product_planter_sizes = None
                product_litres = None
                product_colors = None

                filter_params = {}
                current_product = Product.objects.filter(id=pk).first()
                product_id = current_product.product_id
                filter_params = {'product_id': product_id, 'visible_online': True}

                planter_size_id = request.query_params.get('planter_size_id', None)
                color_id = request.query_params.get('color_id', None)
                litre_id = request.query_params.get('litre_id', None)
                print('pot-----------------',planter_size_id,color_id,litre_id)
                
                filter_params = {'product_id': product_id, 'visible_online': True}
                
                # 1. If only planter_size_id is provided, return available colors for the selected planter_size_id
                if planter_size_id and not color_id and not litre_id:
                    filter_params['planter_size_id'] = planter_size_id

                    product = Product.objects.filter(**filter_params).first()
                    if not product:
                        return Response(data={'message': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    product_planter_size_ids  = Product.objects.filter(product_id=product_id, visible_online=True).values_list('planter_size_id', flat=True).distinct()
                    product_color_ids = Product.objects.filter(**filter_params).values_list('color_id', flat=True).distinct()
                    filter_params['color_id'] = product_color_ids[0]

                    product_planter_sizes = PlanterSizeSerializer(PlanterSize.objects.filter(id__in=product_planter_size_ids), many=True)
                    product_colors = ColorSerializer(Color.objects.filter(id__in=product_color_ids), many=True)
                    
                # 2. If only litre is provided, return available colors for the selected litre
                elif litre_id and not color_id and not planter_size_id:

                    filter_params['litre_id'] = litre_id
                    product = Product.objects.filter(**filter_params).first()
                    if not product:
                        return Response(data={'message': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    product_litre_ids = Product.objects.filter(product_id=product_id, visible_online=True).values_list('litre_id', flat=True).distinct()
                    product_color_ids = Product.objects.filter(**filter_params).values_list('color_id', flat=True).distinct()
                    filter_params['color_id'] = product_color_ids[0]

                    product_litres = LitreSerializer(Litre.objects.filter(id__in=product_litre_ids), many=True)
                    product_colors = ColorSerializer(Color.objects.filter(id__in=product_color_ids), many=True)

                # 3. If planter_size_id and color_id are provided, find the corresponding product
                elif planter_size_id and color_id and not litre_id:
                    filter_params['planter_size_id'] = planter_size_id
                    filter_params['color_id'] = color_id
                    product = Product.objects.filter(**filter_params).first()
                    if not product:
                        return Response(data={'message': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    product_planter_size_ids = Product.objects.filter(product_id=product_id, visible_online=True).values_list('planter_size_id', flat=True).distinct()
                    product_color_ids =  Product.objects.filter(product_id=product_id, planter_size_id=product.planter_size_id, visible_online=True).values_list('color_id', flat=True).distinct()

                    product_planter_sizes = PlanterSizeSerializer(PlanterSize.objects.filter(id__in=product_planter_size_ids), many=True)
                    product_colors = ColorSerializer(Color.objects.filter(id__in=product_color_ids), many=True)

                # 4. If litre and color_id are provided, find the corresponding product
                elif litre_id and color_id and not planter_size_id:
                    filter_params['litre_id'] = litre_id
                    filter_params['color_id'] = color_id
                    product = Product.objects.filter(**filter_params).first()
                    if not product:
                        return Response(data={'message': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
                    
                    product_litre_ids = Product.objects.filter(product_id=product_id, visible_online=True).values_list('litre_id', flat=True).distinct()
                    product_color_ids =  Product.objects.filter(product_id=product_id, litre_id=product.litre_id, visible_online=True).values_list('color_id', flat=True).distinct()

                    product_litres = LitreSerializer(Litre.objects.filter(id__in=product_litre_ids), many=True)
                    product_colors = ColorSerializer(Color.objects.filter(id__in=product_color_ids), many=True)
                else:
                    return Response(data={'message': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)
                
                product = Product.objects.filter(**filter_params).first()
                serializer = ProductSerializer(product, context={'request': request})
                data = {
                    'product_type': product_type,
                    'product': serializer.data,
                    'product_planter_sizes': product_planter_sizes.data if product_planter_sizes else [],
                    'product_litres': product_litres.data if product_litres else [],
                    'product_colors': product_colors.data if product_colors else [],
                }
                return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
            
            elif product_type == 'tool':
                product_sizes = None
                product_colors = None

                filter_params = {}
                current_product = Product.objects.filter(id=pk).first()
                product_id = current_product.product_id
                filter_params = {'product_id': product_id, 'visible_online': True}

                size_id = request.query_params.get('size_id', None)
                color_id = request.query_params.get('color_id', None)
                print('tool-----------------', size_id, color_id)

                # 1. If only size_id is provided, return available colors for that size
                if size_id and not color_id:
                    filter_params['size_id'] = size_id
                    product = Product.objects.filter(**filter_params).first()
                    if not product:
                        return Response(data={'message': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

                    product_size_ids = Product.objects.filter(product_id=product_id, visible_online=True).values_list('size_id', flat=True).distinct()
                    product_color_ids = Product.objects.filter(**filter_params).values_list('color_id', flat=True).distinct()
                    filter_params['color_id'] = product_color_ids[0] if product_color_ids else None

                    product_sizes = SizeSerializer(Size.objects.filter(id__in=product_size_ids), many=True)
                    product_colors = ColorSerializer(Color.objects.filter(id__in=product_color_ids), many=True)

                # 2. If only color_id is provided, return available sizes for that color
                elif color_id and not size_id:
                    filter_params['color_id'] = color_id
                    product = Product.objects.filter(**filter_params).first()
                    if not product:
                        return Response(data={'message': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

                    product_color_ids = Product.objects.filter(product_id=product_id, visible_online=True).values_list('color_id', flat=True).distinct()
                    product_size_ids = Product.objects.filter(**filter_params).values_list('size_id', flat=True).distinct()
                    filter_params['size_id'] = product_size_ids[0] if product_size_ids else None

                    product_colors = ColorSerializer(Color.objects.filter(id__in=product_color_ids), many=True)
                    product_sizes = SizeSerializer(Size.objects.filter(id__in=product_size_ids), many=True)

                # 3. If both size_id and color_id are provided, find the corresponding product
                elif size_id and color_id:
                    filter_params['size_id'] = size_id
                    filter_params['color_id'] = color_id
                    product = Product.objects.filter(**filter_params).first()
                    if not product:
                        return Response(data={'message': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

                    product_size_ids = Product.objects.filter(product_id=product_id, visible_online=True).values_list('size_id', flat=True).distinct()
                    product_color_ids = Product.objects.filter(product_id=product_id, size_id=product.size_id, visible_online=True).values_list('color_id', flat=True).distinct()

                    product_sizes = SizeSerializer(Size.objects.filter(id__in=product_size_ids), many=True)
                    product_colors = ColorSerializer(Color.objects.filter(id__in=product_color_ids), many=True)
                
                else:
                    return Response(data={'message': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

                product = Product.objects.filter(**filter_params).first()
                serializer = ProductSerializer(product, context={'request': request})

                data = {
                    'product_type': product_type,
                    'product': serializer.data,
                    'product_sizes': product_sizes.data if product_sizes else [],
                    'product_colors': product_colors.data if product_colors else [],
                }

                return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)

        return Response(data={'message': 'Product does not exist.'}, status=status.HTTP_400_BAD_REQUEST)