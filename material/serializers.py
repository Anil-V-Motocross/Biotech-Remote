from rest_framework import serializers
from .models import (
    InventoryItem, InventoryItemImage, PotVariant, PotVariantImage,
    ToolVariant, ToolVariantImage, Rating, Review, Material, Shape, PotType, HandleMaterial, BladeMaterial
)
from attribute.models import Color, Size

class InventoryItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = InventoryItemImage
        fields = ['image']

class PotVariantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = PotVariantImage
        fields = ['image']

class ToolVariantImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ToolVariantImage
        fields = ['image']

class PotVariantSerializer(serializers.ModelSerializer):
    images = PotVariantImageSerializer(many=True, required=False)
    
    class Meta:
        model = PotVariant
        fields = ['size', 'color', 'pot_type', 'litre', 'mrp', 'sale_price', 'discount', 'stock', 'images']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        pot_variant = PotVariant.objects.create(**validated_data)
        for img_data in images_data:
            PotVariantImage.objects.create(pot_variant=pot_variant, **img_data)
        return pot_variant

class ToolVariantSerializer(serializers.ModelSerializer):
    images = ToolVariantImageSerializer(many=True, required=False)

    class Meta:
        model = ToolVariant
        fields = ['size', 'color', 'handle_material', 'blade_material', 'mrp', 'sale_price', 'discount', 'stock', 'images']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        tool_variant = ToolVariant.objects.create(**validated_data)
        for img_data in images_data:
            ToolVariantImage.objects.create(tool_variant=tool_variant, **img_data)
        return tool_variant

class InventoryItemSerializer(serializers.ModelSerializer):
    images = InventoryItemImageSerializer(many=True, required=False)
    pot_variants = PotVariantSerializer(many=True, required=False)
    tool_variants = ToolVariantSerializer(many=True, required=False)

    class Meta:
        model = InventoryItem
        fields = [
            'name', 'category', 'material', 'shape', 'short_description', 'long_description', 'mrp', 'sale_price', 
            'discount', 'whats_in_the_box', 'additional_attributes', 'images', 'pot_variants', 'tool_variants'
        ]

    def to_representation(self, instance):
        """Modify response to reorder images based on variant selection"""
        data = super().to_representation(instance)
        
        # Default Inventory Images
        inventory_images = data.get('images', [])
        
        # Collect images from Pot Variants
        pot_variant_images = []
        for pot_variant in data.get('pot_variants', []):
            if 'images' in pot_variant:
                pot_variant_images.extend(pot_variant['images'])

        # Collect images from Tool Variants
        tool_variant_images = []
        for tool_variant in data.get('tool_variants', []):
            if 'images' in tool_variant:
                tool_variant_images.extend(tool_variant['images'])

        # Merge Images (Variant Images First)
        all_images = pot_variant_images + tool_variant_images + inventory_images

        # Update final images list
        data['images'] = all_images
        
        return data

class FilteredInventorySerializer(serializers.ModelSerializer):
    images = InventoryItemImageSerializer(many=True, required=False)

    class Meta:
        model = InventoryItem
        fields = [
            'name', 'category', 'material', 'shape', 'short_description', 'long_description', 
            'mrp', 'sale_price', 'discount', 'whats_in_the_box', 'additional_attributes', 
            'images'
        ]

    def to_representation(self, instance):
        """Modify response to include selected variant's price, stock, and images"""
        data = super().to_representation(instance)
        selected_variant = self.context.get('selected_variant')

        # Get inventory item images
        inventory_images = InventoryItemImage.objects.filter(inventory_item=instance)
        inventory_images_serialized = InventoryItemImageSerializer(inventory_images, many=True).data

        all_variant_images_serialized = []
        
        if selected_variant:
            # Apply pricing & stock updates
            data['mrp'] = selected_variant.mrp
            data['sale_price'] = selected_variant.sale_price
            data['discount'] = selected_variant.discount
            data['stock'] = selected_variant.stock

            # Get selected variant images
            selected_variant_images = []
            if hasattr(selected_variant, 'images'):
                selected_variant_images = InventoryItemImageSerializer(selected_variant.images.all(), many=True).data
            
            # Fetch images from all other variants of the same inventory item
            all_variants = selected_variant.__class__.objects.filter(inventory_item=instance).exclude(id=selected_variant.id)
            all_variant_items = InventoryItem.objects.filter(id__in=all_variants.values_list('inventory_item_id', flat=True))
            all_variant_images = InventoryItemImage.objects.filter(inventory_item__in=all_variant_items)
            all_variant_images_serialized = InventoryItemImageSerializer(all_variant_images, many=True).data

            # Merge images: selected variant → inventory item → other variants
            data['images'] = selected_variant_images + inventory_images_serialized + all_variant_images_serialized
        else:
            # If no variant is selected, return only inventory item images
            data['images'] = inventory_images_serialized

        return data


class RatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Rating
        fields = ['user', 'product_rating', 'date']

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField()

    class Meta:
        model = Review
        fields = ['user', 'product_review', 'date']

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
        model = BladeMaterial
        fields = ['id', 'name']

class ToolVariantSerializer(serializers.ModelSerializer):
    inventory_item = serializers.StringRelatedField()
    size = serializers.StringRelatedField(allow_null=True)
    color = serializers.StringRelatedField(allow_null=True)
    handle_material = HandleMaterialSerializer(allow_null=True)
    blade_material = BladeMaterialSerializer(allow_null=True)

    class Meta:
        model = ToolVariant
        fields = [
            'id', 'inventory_item', 'size', 'color', 'handle_material', 'blade_material',
            'mrp', 'sale_price', 'discount', 'profit', 'stock', 'visible_online', 'date_added'
        ]        