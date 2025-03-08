from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from product.models import Product
from rest_framework import serializers
from product.models import Product, MainProductImage, Rating, Review,MainProduct
from django.conf import settings
from attribute.models import Size
from attribute.models import PlanterSize, Weight
from attribute.models import Planter
from attribute.models import Color
from attribute.models import Material, HandleMaterial, BladeMaterial, Shape, PotType, Litre
from django.db.models import Avg, Count, F
from django.db.models.functions import Floor
from product.serializers import AddOnProductSerializer
from order.models import Cart, Wishlist, OrderItem

class ReviewSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(format='%d/%m/%Y')
    latest_rating = serializers.SerializerMethodField()
    user_name = serializers.CharField(source='user_id.first_name', read_only=True)  # Access the related field


    class Meta:
        model = Review
        fields = ['id', 'user_id', 'user_name', 'product_review', 'date', 'latest_rating']

    def get_latest_rating(self, obj):
        # Retrieve the latest rating for the product and user
        rating = Rating.objects.filter(
            main_product_id=obj.main_product_id, user_id=obj.user_id
            ).order_by('-date').first()

        return rating.product_rating if rating else None

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

class HandleMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = HandleMaterial
        fields = ['id', 'name']   

class BladeMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ['id', 'name']   

class LitreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Litre
        fields = ['id', 'name']

class AddProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainProduct
        fields = ['id', 'name', 'default_sale_price', 'default_price']

class ProductSerializer(serializers.ModelSerializer):
    # type = serializers.ReadOnlyField(source='product_id.type')
    # Include main product image as the first element in the images list
    images = serializers.SerializerMethodField()
    # add short_description from MainProduct
    short_description = serializers.ReadOnlyField(source='product_id.short_description')
    main_product_name = serializers.ReadOnlyField(source='product_id.name')
    whats_included = serializers.ReadOnlyField(source='product_id.whats_included')
    vedio_link = serializers.ReadOnlyField(source='product_id.vedio_link')
    mrp = serializers.FloatField(source='sale_price')
    is_cart = serializers.SerializerMethodField()
    is_wishlist = serializers.SerializerMethodField()
    is_purchased = serializers.SerializerMethodField()
    class Meta:
        model = Product
        fields = [
            'id', 
            'mrp',
            'price', 
            'is_cart',
            'is_wishlist',
            'images', 
            'short_description', 
            'main_product_name', 
            'size_id', 
            'planter_size_id', 
            'planter_id',
            'weight_id', 
            # 'handle_material_id',
            # 'blade_material_id',
            # 'material_id',
            # 'shape_id',
            # 'pot_type_id',
            'litre_id',
            'color_id', 
            'whats_included', 
            'vedio_link',
            'is_purchased'
        ]


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
 
    def get_is_purchased(self, obj):
        """Check if the product was purchased by the user and has a delivered order status."""
        user = self.context.get('request').user
        if user.is_authenticated:
            return OrderItem.objects.filter(
                product_id=obj,
                order_id__customer_id=user,
                order_id__status="delivered"  # Ensures the order is delivered
            ).exists()
        return False

@api_view(['GET'])
def default_product(request, product_id=None):
    if request.method == 'GET' and product_id:
        # Filter the product to get the default one with the specified product_id
        product = Product.objects.filter(product_id=product_id, is_default=True).first()
        
        # Check if the product exists
        if product is None:
            return Response(data={'message': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the single product (do not use `many=True`)
        serializer = ProductSerializer(product, context={'request': request})

        # return the product type
        product_type = product.product_id.type

        product_add_ons = AddOnProductSerializer(product.product_id.add_ons.all()[:3], many=True, context={'request': request})
        
        # return all unique size_id of the product
        product_size_ids = Product.objects.filter(product_id=product_id, visible_online=True).values_list('size_id', flat=True).distinct()
        product_planter_size_ids = Product.objects.filter(product_id=product_id, size_id=product.size_id,  visible_online=True).values_list('planter_size_id', flat=True).distinct()
        product_planter_ids = Product.objects.filter(product_id=product_id, size_id=product.size_id, planter_size_id=product.planter_size_id, visible_online=True).values_list('planter_id', flat=True).distinct()
        product_color_ids = Product.objects.filter(product_id=product_id, size_id=product.size_id, planter_size_id=product.planter_size_id, planter_id=product.planter_id, visible_online=True).values_list('color_id', flat=True).distinct()
        product_weight_ids = Product.objects.filter(product_id=product_id, size_id=product.size_id, planter_size_id=product.planter_size_id, planter_id=product.planter_id, color_id=product.color_id, visible_online=True).values_list('weight_id', flat=True).distinct()

        product_sizes = SizeSerializer(Size.objects.filter(id__in=product_size_ids), many=True)
        product_planter_sizes = PlanterSizeSerializer(PlanterSize.objects.filter(id__in=product_planter_size_ids), many=True)
        product_planter = PlanterSerializer(Planter.objects.filter(id__in=product_planter_ids), many=True)
        product_color = ColorSerializer(Color.objects.filter(id__in=product_color_ids), many=True)
        product_weights = WeightSerializer(Weight.objects.filter(id__in=product_weight_ids), many=True) if product_weight_ids else None
        
        # Tool and Pot-specific fields
        # handle_material = HandleMaterialSerializer(product.handle_material_id) if product.handle_material_id else None
        # blade_material = BladeMaterialSerializer(product.blade_material_id) if product.blade_material_id else None
        # material = MaterialSerializer(product.material_id) if product.material_id else None
        # shape = ShapeSerializer(product.shape_id) if product.shape_id else None
        # pot_type = PotTypeSerializer(product.pot_type_id) if product.pot_type_id else None
        litre_ids = Product.objects.filter(product_id=product_id, visible_online=True).values_list('litre_id', flat=True).distinct()
        product_litres = LitreSerializer(Litre.objects.filter(id__in=litre_ids), many=True)

        # return rating by calulating average of product_rating 
        product_rating = Rating.objects.filter(main_product_id=product_id).aggregate(avg_rating=Avg('product_rating'), num_ratings=Count('id'))
        product_rating['avg_rating'] = round(product_rating['avg_rating'], 2) if product_rating['avg_rating'] else 0
        
        # return number of stars given by user for the product like 5 starts is given 10 users, 4 starts is given by 5 users like {'5': 10, '4': 5}
        product_rating['stars_given'] = (Rating.objects.filter(main_product_id=product_id).annotate(rounded_rating=Floor(F('product_rating')))
                                         .values('rounded_rating').annotate(count=Count('id')).order_by('-rounded_rating'))
        
        # return product review by user
        product_reviews = Review.objects.filter(main_product_id=product_id)
        product_reviews = ReviewSerializer(product_reviews, many=True)
        
        # Prepare the response data
        data = {
            'product_type': product_type,
            'product': serializer.data,
            'product_sizes': product_sizes.data,
            'product_planter_sizes': product_planter_sizes.data,
            'product_weights': product_weights.data,
            'product_planters': product_planter.data,
            'product_litres': product_litres.data,
            'product_colors': product_color.data,
            # 'product_handle_material': handle_material.data if handle_material else None,
            # 'product_blade_material': blade_material.data if blade_material else None,
            # 'product_material': material.data if material else None,
            # 'product_shape': shape.data if shape else None,
            # 'product_pot_type': pot_type.data if pot_type else None,
            'product_rating': product_rating,
            'product_reviews': product_reviews.data,
            'product_add_ons': product_add_ons.data,
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)

    return Response(data={'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)
