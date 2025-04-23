from rest_framework import serializers
from product.models import MainProduct, MainProductImage, Rating, Review
from django.db.models import Avg, Count, F
from django.db.models.functions import Floor
from order.models import Order
from order.models import Cart, Wishlist
from product.models import Product
from django.conf import settings


class MainProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    product_rating = serializers.SerializerMethodField()
    mrp = serializers.FloatField(source='default_mrp')
    selling_price = serializers.FloatField(source='default_selling_price')
    is_cart = serializers.SerializerMethodField()
    is_wishlist = serializers.SerializerMethodField()

    class Meta:
        model = MainProduct
        fields = ['id', 'name', 'is_cart', 'is_wishlist', 'mrp', 'selling_price', 'image', 'product_rating']

    def get_image(self, obj):
        image = MainProductImage.objects.filter(product=obj).first()
        return image.image.url if image else None

    def get_product_rating(self, obj):
        product_rating = Rating.objects.filter(main_product_id=obj.id).aggregate(
            avg_rating=Avg('product_rating'),
            num_ratings=Count('id')
        )
        product_rating['avg_rating'] = round(product_rating['avg_rating'], 2) if product_rating['avg_rating'] else 0

        # Breakdown of star ratings
        stars_given = list(
            Rating.objects.filter(main_product_id=obj.id)
            .annotate(rounded_rating=Floor(F('product_rating')))
            .values('rounded_rating')
            .annotate(count=Count('id'))
            .order_by('-rounded_rating')
        )

        # Convert queryset to required list format
        # product_rating['stars_given'] = [{"stars": entry["rounded_rating"], "count": entry["count"]} for entry in stars_given]

        return product_rating

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

class AddOnProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    product_rating = serializers.SerializerMethodField()
    selling_price = serializers.FloatField(source='default_selling_price')
    mrp = serializers.FloatField(source='default_mrp')
    is_cart = serializers.SerializerMethodField()
    is_wishlist = serializers.SerializerMethodField()

    class Meta:
        model = MainProduct
        fields = ['id', 'name', 'mrp', 'selling_price', 'image', 'product_rating', 'is_cart', 'is_wishlist']

    def get_image(self, obj):
        image = MainProductImage.objects.filter(product=obj).first()
        return image.image.url if image else None

    def get_product_rating(self, obj):
        product_rating = Rating.objects.filter(main_product_id=obj.id).aggregate(
            avg_rating=Avg('product_rating'),
            num_ratings=Count('id')
        )
        product_rating['avg_rating'] = round(product_rating['avg_rating'], 2) if product_rating['avg_rating'] else 0

        # Breakdown of star ratings
        stars_given = list(
            Rating.objects.filter(main_product_id=obj.id)
            .annotate(rounded_rating=Floor(F('product_rating'))).values('rounded_rating')
            .annotate(count=Count('id')).order_by('-rounded_rating')
        )

        # product_rating['stars_given'] = [{"stars": entry["rounded_rating"], "count": entry["count"]} for entry in stars_given]

        return product_rating

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

    # def get_product_id(self, obj):
    #     """Retrieve the ID of the default product for this MainProduct."""
    #     default_product = obj.product_set.filter(is_default=True).first()  # Fetch the default product
    #     return default_product.id if default_product else None  




class RatingReviewSerializer(serializers.Serializer):
    main_product_id = serializers.IntegerField()
    product_rating = serializers.DecimalField(max_digits=3, decimal_places=2, required=False)
    review_title = serializers.CharField(max_length=50, required=False)
    product_review = serializers.CharField(max_length=300, required=False)
    recommend = serializers.BooleanField(required=False)

    def validate(self, data):
        user = self.context['request'].user
        product_id = data.get('main_product_id')

        if self.context['request'].method == 'POST':

            products = Product.objects.filter(product_id=product_id).values_list('id', flat=True)

            # Ensure the user has purchased and received the product
            orders = Order.objects.filter(
                customer_id=user,
                orderitem__product_id__in=products  # ✅ Now filtering with a list of product IDs
            ).distinct()

            if not orders.exists():
                raise serializers.ValidationError("You have not purchased this product.")

            # Check if the product was delivered
            delivered_orders = orders.filter(status_history__status="DELIVERED").distinct()

            if not delivered_orders.exists():
                raise serializers.ValidationError("You can only review this product after delivery.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        product_id = validated_data['main_product_id']

        # Handle Rating
        rating = validated_data.get('product_rating')
        if rating is not None:
            rating_obj, _ = Rating.objects.update_or_create(
                main_product_id_id=product_id,
                user_id=user,
                defaults={'product_rating': rating}
            )

        # Handle Review
        review_text = validated_data.get('product_review')
        review_title = validated_data.get('review_title')
        recommend = validated_data.get('recommend', True) 

        if review_text or review_title:
            review_obj, _ = Review.objects.update_or_create(
                main_product_id_id=product_id,
                user_id=user,
                defaults={
                    'review_title': review_title,
                    'product_review': review_text,
                    'recommend': recommend
                }
            )

        return {"message": "Rating and/or review submitted successfully."}
    
class MainProductMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainProduct
        fields = ['id', 'name']

class ProductMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name']


class ProductInventorySerializer(serializers.ModelSerializer):

    # Convert ForeignKey IDs to their names
    size = serializers.CharField(source='size_id.name', required=False, allow_null=True)
    planter_size = serializers.CharField(source='planter_size_id.name', required=False, allow_null=True)
    planter = serializers.CharField(source='planter_id.name', required=False, allow_null=True)
    color = serializers.CharField(source='color_id.color_name', required=False, allow_null=True)
    weight = serializers.CharField(source='weight_id.size_grams', required=False, allow_null=True)
    litre = serializers.CharField(source='litre_id.name', required=False, allow_null=True)
    
    class Meta:
        model = Product
        fields = [
            'name', 'stock', 'cost', 'selling_price', 'mrp', 'profit', 'discount', 'sku', 'image',
            'date_added', 'size', 'planter_size', 'planter', 'color', 'weight', 'litre',
        ]        
   

class ProductSerializer(serializers.ModelSerializer):
    id = serializers.CharField(source='product_id.id')
    image = serializers.SerializerMethodField()
    name = serializers.ReadOnlyField(source='product_id.name')
    is_cart = serializers.SerializerMethodField()
    is_wishlist = serializers.SerializerMethodField()
    product_rating = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ['id', 'name', 'is_cart', 'is_wishlist', 'mrp', 'selling_price', 'image', 'product_rating']

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
    
    def get_product_rating(self, obj):
        product_rating = Rating.objects.filter(main_product_id=obj.product_id.id).aggregate(
            avg_rating=Avg('product_rating'),
            num_ratings=Count('id')
        )
        product_rating['avg_rating'] = round(product_rating['avg_rating'], 2) if product_rating['avg_rating'] else 0

        # Breakdown of star ratings
        stars_given = list(
            Rating.objects.filter(main_product_id=obj.product_id.id)
            .annotate(rounded_rating=Floor(F('product_rating')))
            .values('rounded_rating')
            .annotate(count=Count('id'))
            .order_by('-rounded_rating')
        )

        return product_rating
    
    def get_image(self, obj):
        """
        Returns the relative path of the first main product image.
        Fallback to product.image if no MainProductImage is found.
        """
        # Try MainProductImage first
        main_image = MainProductImage.objects.filter(product=obj.product_id).first()
        if main_image and main_image.image:
            return main_image.image.url  # returns '/media/...'

        # Fallback to Product.image
        if obj.image:
            return obj.image.url

        return None    