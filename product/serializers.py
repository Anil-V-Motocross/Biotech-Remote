from rest_framework import serializers
from product.models import MainProduct, MainProductImage, Rating, Review
from django.db.models import Avg, Count, F
from django.db.models.functions import Floor
from order.models import Order
from order.models import Cart, Wishlist
from product.models import Product

class MainProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()
    product_rating = serializers.SerializerMethodField()
    mrp = serializers.FloatField(source='default_sale_price')
    price = serializers.FloatField(source='default_price')
    is_cart = serializers.SerializerMethodField()
    is_wishlist = serializers.SerializerMethodField()

    class Meta:
        model = MainProduct
        fields = ['id', 'name', 'is_cart', 'is_wishlist', 'mrp', 'price', 'image', 'product_rating']

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
    price = serializers.FloatField(source='default_price')
    mrp = serializers.FloatField(source='default_sale_price')


    class Meta:
        model = MainProduct
        fields = ['id', 'name', 'mrp', 'price', 'image', 'product_rating']

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

    def get_product_id(self, obj):
        """Retrieve the ID of the default product for this MainProduct."""
        default_product = obj.product_set.filter(is_default=True).first()  # Fetch the default product
        return default_product.id if default_product else None  




class RatingReviewSerializer(serializers.Serializer):
    main_product_id = serializers.IntegerField()
    product_rating = serializers.DecimalField(max_digits=3, decimal_places=2, required=False)
    product_review = serializers.CharField(required=False)

    def validate(self, data):
        user = self.context['request'].user  # Get logged-in user
        product_id = data.get('main_product_id')

        # Check if the user has an order for this product
        orders = Order.objects.filter(
            customer_id=user,
            orderitem__product_id__product_id=product_id  # Linking Order -> OrderItem -> Product -> MainProduct
        ).distinct()

        if not orders.exists():
            raise serializers.ValidationError("You have not purchased this product.")

        # Check if the product was delivered
        delivered_orders = orders.filter(shipment__shipment_status="Delivered")

        if not delivered_orders.exists():
            raise serializers.ValidationError("You can only review this product after delivery.")

        return data

    def create(self, validated_data):
        user = self.context['request'].user
        product_id = validated_data['main_product_id']

        # Handle Rating
        rating = validated_data.get('product_rating')
        if rating is not None:
            rating_obj, created = Rating.objects.update_or_create(
                main_product_id_id=product_id,
                user_id=user,
                defaults={'product_rating': rating}
            )

        # Handle Review
        review_text = validated_data.get('product_review')
        if review_text:
            review_obj, created = Review.objects.update_or_create(
                main_product_id_id=product_id,
                user_id=user,
                defaults={'product_review': review_text}
            )

        return {"message": "Rating and/or review submitted successfully."}
    
class MainProductMinimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainProduct
        fields = ['id', 'name']
