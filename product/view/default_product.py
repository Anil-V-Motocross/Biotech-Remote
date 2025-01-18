from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from product.models import Product
from rest_framework import serializers
from product.models import Product, MainProductImage, Rating, Review
from django.conf import settings
from attribute.models import Size
from attribute.models import PlanterSize
from attribute.models import Planter
from attribute.models import Color
from django.db.models import Avg, Count, F
from django.db.models.functions import Floor

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

class ProductSerializer(serializers.ModelSerializer):
    # Include main product image as the first element in the images list
    images = serializers.SerializerMethodField()
    # add short_description from MainProduct
    short_description = serializers.ReadOnlyField(source='product_id.short_description')
    main_product_name = serializers.ReadOnlyField(source='product_id.name')
    whats_included = serializers.ReadOnlyField(source='product_id.whats_included')
    vedio_link = serializers.ReadOnlyField(source='product_id.vedio_link')

    class Meta:
        model = Product
        fields = ['id', 'price', 'images', 'short_description', 'main_product_name', 'size_id', 'planter_size_id', 'planter_id', 'color_id', 'whats_included', 'vedio_link']

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
    if request.method == 'GET' and product_id:
        # Filter the product to get the default one with the specified product_id
        product = Product.objects.filter(product_id=product_id, is_default=True).first()
        
        # Check if the product exists
        if product is None:
            return Response(data={'message': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # Serialize the single product (do not use `many=True`)
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
            'product': serializer.data,
            'product_sizes': product_sizes.data,
            'product_planter_sizes': product_planter_sizes.data,
            'product_planters': product_planter.data,
            'product_colors': product_color.data,
            'product_rating': product_rating,
            'product_reviews': product_reviews.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)

    return Response(data={'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)
