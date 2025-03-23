from rest_framework import serializers
from product.models import Product, Rating, Color, Size, PlanterSize, Planter, Weight, Material, Shape, PotType, HandleMaterial, BladeMaterial, Litre
from django.conf import settings
from django.db.models import Avg, Count
from order.models import Cart, Wishlist
from product.models import MainProduct

class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='product_id.id', read_only=True)
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    product_rating = serializers.SerializerMethodField()
    is_cart = serializers.SerializerMethodField()
    is_wishlist = serializers.SerializerMethodField()
    # color = serializers.CharField(source="color_id.color_name", allow_null=True, default=None)
    # size = serializers.CharField(source="size_id.name", allow_null=True, default=None)
    # planter_size = serializers.CharField(source="planter_size_id.name", allow_null=True, default=None)
    # planter = serializers.CharField(source="planter_id.name", allow_null=True, default=None)
    # weight = serializers.CharField(source="weight_id.size_grams", allow_null=True, default=None)
    # litre = serializers.CharField(source="litre_id.name", allow_null=True, default=None)
    # material = serializers.CharField(source="material_id.name", allow_null=True, default=None)
    # shape = serializers.CharField(source="shape_id.name", allow_null=True, default=None)
    # pot_type = serializers.CharField(source="pot_type_id.name", allow_null=True, default=None)
    # handle_material = serializers.CharField(source="handle_material_id.name", allow_null=True, default=None)
    # blade_material = serializers.CharField(source="blade_material_id.name", allow_null=True, default=None)

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "mrp",
            "selling_price",
            "image",
            "is_cart",
            "is_wishlist",
            "product_rating",
            # "size",
            # "planter_size",
            # "planter",
            # "weight",
            # "litre",
            # "color",
            # "material",
            # "shape",
            # "pot_type",
            # "handle_material",
            # "blade_material",
        ]

    def get_name(self, obj):
        """Concatenates MainProduct name and Product name."""
        return f"{obj.product_id.name} {obj.name}" if obj.product_id else obj.name
    
    def get_image(self, obj):
        """Returns the relative path of the image instead of the full URL."""
        if obj.image:
            return f"{settings.MEDIA_URL}{obj.image.name}"  
        return None  

    def get_product_rating(self, obj):
        product_rating = Rating.objects.filter(main_product_id=obj.product_id).aggregate(
            avg_rating=Avg('product_rating'),
            num_ratings=Count('id')
        )
        product_rating['avg_rating'] = round(product_rating['avg_rating'], 2) if product_rating['avg_rating'] else 0

        return product_rating  

    def get_is_cart(self, obj):
        """Check if the product exists in the user's cart."""        
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:
            product_instance = Product.objects.filter(name=obj).first()

            if product_instance:
                exists = Cart.objects.filter(user_id=request.user, product_id=product_instance).exists()
                return exists

        return False

    def get_is_wishlist(self, obj):
        """Check if the product exists in the user's wishlist."""     
        request = self.context.get('request', None)
        if request and request.user.is_authenticated:           
            product_instance = Product.objects.filter(name=obj).first()

            if product_instance:
                exists = Wishlist.objects.filter(user_id=request.user, product_id=product_instance).exists()
                return exists

        return False
