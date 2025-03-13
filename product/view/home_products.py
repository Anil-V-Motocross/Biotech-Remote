from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from product.models import MainProduct, MainProductImage, Product
from rest_framework import serializers
from order.models import Cart, Wishlist
from django.conf import settings
from django.db.models import Avg, Count, F
from product.models import Rating

# class MainProductImageSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = MainProductImage
#         fields = ['id', 'image']


class MainProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()  # Override image field to return correct format

    class Meta:
        model = MainProductImage
        fields = ['id', 'image']

    def get_image(self, obj):
        """Return the relative media URL instead of the full absolute URL."""
        if obj.image:
            return f"{settings.MEDIA_URL}{obj.image.name}"  # Only return the media path
        return None


# Serializer for MainProduct, with related images
class MainProductSerializer(serializers.ModelSerializer):
    images = MainProductImageSerializer(many=True, read_only=True)  # Include related images
    is_cart = serializers.SerializerMethodField()
    is_wishlist = serializers.SerializerMethodField()
    product_rating = serializers.SerializerMethodField()

    class Meta:
        model = MainProduct
        fields = ['id', 'name', 'is_featured', 'is_best_seller', 'is_seasonal_collection', 'is_trending', 'images', 'is_cart', 'is_wishlist', 'product_rating']

    def to_representation(self, instance):
        # Call the parent class to get the default representation
        representation = super().to_representation(instance)

        # Get the first image from the images list, if any
        if representation['images']:
            representation['image'] = representation['images'][0]['image']
        else:
            representation['image'] = None  # If no images, set image to None

        default_product = instance.product_set.filter(is_default=True).first()

        if default_product:
            representation['price'] = default_product.price
            representation['mrp'] = default_product.sale_price
        else:
            representation['price'] = None
            representation['mrp'] = None

        # Optionally, remove the 'images' field if you don't need it in the response
        representation.pop('images', None)

        return representation

    def get_is_cart(self, obj):
        """Check if the product exists in the user's cart."""
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            # Get the default product (variant) of this MainProduct
            product_instance = Product.objects.filter(product_id=obj, is_default=True).first()
            
            if product_instance:
                return Cart.objects.filter(user_id=request.user, product_id=product_instance).exists()
        return False

    def get_is_wishlist(self, obj):
        """Check if the product exists in the user's wishlist."""
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            # Get the default product (variant) of this MainProduct
            product_instance = Product.objects.filter(product_id=obj, is_default=True).first()
            
            if product_instance:
                return Wishlist.objects.filter(user_id=request.user, product_id=product_instance).exists()
        return False

    def get_product_rating(self, obj):
        product_rating = Rating.objects.filter(main_product_id=obj.id).aggregate(
            avg_rating=Avg('product_rating'),
            num_ratings=Count('id')
        )
        product_rating['avg_rating'] = round(product_rating['avg_rating'], 2) if product_rating['avg_rating'] else 0

        return product_rating

@api_view(['GET'])
def home_products(request):
    if request.method == 'GET':
        products = MainProduct.objects.all()
        serializer = MainProductSerializer(products, many=True, context={'request': request})
        data = {
            'products': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)

    return Response(data={'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)