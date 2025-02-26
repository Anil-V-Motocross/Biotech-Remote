from django.db.models import Count, Avg
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, serializers
from .models import (
    InventoryItem, Rating, Review, Material, BladeMaterial, HandleMaterial, 
    Shape, PotType, PotVariant, ToolVariant
)
from .serializers import (
    InventoryItemSerializer, ReviewSerializer, PotVariantSerializer, 
    MaterialSerializer, ShapeSerializer, PotTypeSerializer, 
    ToolVariantSerializer, HandleMaterialSerializer, BladeMaterialSerializer,
    FilteredInventorySerializer
)
from attribute.models import Color, Size

class SizeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Size
        fields = ['id', 'name', 'size']

class ColorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Color
        fields = ['id', 'color_name', 'color_code']

@api_view(['GET'])
def get_inventory_item(request, inventory_item_id=None):
    if request.method == 'GET' and inventory_item_id:
        # Fetch the inventory item
        inventory_item = InventoryItem.objects.filter(id=inventory_item_id).first()
        
        if inventory_item is None:
            return Response(data={'message': 'Inventory item not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        product_type = inventory_item.category
        # Serialize inventory item
        serializer = InventoryItemSerializer(inventory_item, context={'request': request})
        
        # Fetch available sizes and colors for variants
        pot_size_ids = inventory_item.pot_variants.values_list('size_id', flat=True).distinct()
        pot_color_ids = inventory_item.pot_variants.values_list('color_id', flat=True).distinct()
        tool_size_ids = inventory_item.tool_variants.values_list('size_id', flat=True).distinct()
        tool_color_ids = inventory_item.tool_variants.values_list('color_id', flat=True).distinct()
        
        # Serialize sizes and colors
        pot_sizes = SizeSerializer(Size.objects.filter(id__in=pot_size_ids), many=True).data
        pot_colors = ColorSerializer(Color.objects.filter(id__in=pot_color_ids), many=True).data
        tool_sizes = SizeSerializer(Size.objects.filter(id__in=tool_size_ids), many=True).data
        tool_colors = ColorSerializer(Color.objects.filter(id__in=tool_color_ids), many=True).data
        
        # Calculate product rating
        product_rating = Rating.objects.filter(inventory_item=inventory_item).aggregate(
            avg_rating=Avg('product_rating'), num_ratings=Count('id')
        )
        product_rating['avg_rating'] = round(product_rating['avg_rating'], 2) if product_rating['avg_rating'] else 0
        
        # Get count of star ratings 
        product_rating['stars_given'] = (
            Rating.objects.filter(inventory_item=inventory_item)
            .values('product_rating')
            .annotate(count=Count('id'))
            .order_by('-product_rating')
        )
        
        # Fetch product reviews
        product_reviews = Review.objects.filter(inventory_item=inventory_item)
        product_reviews = ReviewSerializer(product_reviews, many=True).data
        
        # Prepare response data
        data = {
            'product_type': product_type,
            'inventory_item': serializer.data,
            'pot_sizes': pot_sizes,
            'pot_colors': pot_colors,
            'tool_sizes': tool_sizes,
            'tool_colors': tool_colors,
            'product_rating': product_rating,
            'product_reviews': product_reviews,
        }
        
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    return Response(data={'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)



@api_view(['GET'])
def filter_inventory(request, pk):
    if not InventoryItem.objects.filter(id=pk).exists():
        return Response(data={'message': 'Inventory item does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

    current_item = InventoryItem.objects.get(id=pk)
    item_type = current_item.category
    filter_params = {'inventory_item': current_item, 'visible_online': True}

    if item_type == 'pot':
        # Get query parameters
        size_id = request.query_params.get('size_id', None)
        litre = request.query_params.get('litre', None)
        color_id = request.query_params.get('color_id', None)

        # Enforce the rule: Either size & color OR litre & color, but not both
        if size_id and litre:
            return Response(data={'message': 'Select either size or litre, not both.'}, status=status.HTTP_400_BAD_REQUEST)

        # Apply filters
        if size_id:
            filter_params['size_id'] = size_id
        if litre:
            filter_params['litre'] = litre
        if color_id:
            filter_params['color_id'] = color_id

        # Fetch filtered variants
        pot_variants = PotVariant.objects.filter(**filter_params)

        if not pot_variants.exists():
            return Response(data={'message': 'No matching pot variant found.'}, status=status.HTTP_400_BAD_REQUEST)

        selected_variant = pot_variants.first()

        # Ensure available_litres and available_sizes are always initialized
        available_sizes = Size.objects.none()  # Default empty queryset
        available_litres = []

        # If size is selected, get available colors for that size
        if size_id:
            available_colors = Color.objects.filter(
                id__in=PotVariant.objects.filter(inventory_item=current_item, size_id=size_id)
                .values_list('color_id', flat=True)
                .distinct()
            )
        # If litre is selected, get available colors for that litre
        elif litre:
            available_colors = Color.objects.filter(
                id__in=PotVariant.objects.filter(inventory_item=current_item, litre=litre)
                .values_list('color_id', flat=True)
                .distinct()
            )
        else:
            # Default to all available colors if no specific size/litre is selected
            available_colors = Color.objects.filter(
                id__in=PotVariant.objects.filter(inventory_item=current_item)
                .values_list('color_id', flat=True)
                .distinct()
            )

        # Get sizes if no litre is selected
        if not litre:
            available_sizes = Size.objects.filter(
                id__in=PotVariant.objects.filter(inventory_item=current_item)
                .values_list('size_id', flat=True)
                .distinct()
            )

        # Get litres if no size is selected
        if not size_id:
            available_litres = list(
                PotVariant.objects.filter(inventory_item=current_item)
                .values_list('litre', flat=True)
                .distinct()
            )

        return Response(data={
            'message': 'success',
            'data': {
                'item_type': item_type,
                'item': FilteredInventorySerializer(current_item, context={'request': request, 'selected_variant': selected_variant}).data,
                'available_sizes': SizeSerializer(available_sizes, many=True).data,
                'available_litres': available_litres,  # List format
                'available_colors': ColorSerializer(available_colors, many=True).data,
            }
        }, status=status.HTTP_200_OK)




    elif item_type == 'tool':
        handle_material_id = request.query_params.get('handle_material_id', None)
        blade_material_id = request.query_params.get('blade_material_id', None)
        size_id = request.query_params.get('size_id', None)
        color_id = request.query_params.get('color_id', None)

        if handle_material_id:
            filter_params['handle_material_id'] = handle_material_id
        if blade_material_id:
            filter_params['blade_material_id'] = blade_material_id
        if size_id:
            filter_params['size_id'] = size_id
        if color_id:
            filter_params['color_id'] = color_id            

        tool_variants = ToolVariant.objects.filter(**filter_params)
        if not tool_variants.exists():
            return Response(data={'message': 'No matching tool variant found.'}, status=status.HTTP_400_BAD_REQUEST)

        selected_variant = tool_variants.first()
        # Retrieve available options for tools
        available_sizes = Size.objects.filter(id__in=ToolVariant.objects.filter(inventory_item=current_item).values_list('size_id', flat=True).distinct())
        available_colors = Color.objects.filter(id__in=ToolVariant.objects.filter(inventory_item=current_item).values_list('color_id', flat=True).distinct())
        available_handle_materials = HandleMaterial.objects.filter(id__in=ToolVariant.objects.filter(inventory_item=current_item).values_list('handle_material_id', flat=True).distinct())
        available_blade_materials = BladeMaterial.objects.filter(id__in=ToolVariant.objects.filter(inventory_item=current_item).values_list('blade_material_id', flat=True).distinct())

        return Response(data={
            'message': 'success',
            'data': {
                'item_type': item_type,
                'item': FilteredInventorySerializer(current_item, context={'request': request, 'selected_variant': selected_variant}).data,
                'available_sizes': SizeSerializer(available_sizes, many=True).data,
                'available_colors': ColorSerializer(available_colors, many=True).data,
                'available_handle_materials': HandleMaterialSerializer(available_handle_materials, many=True).data,
                'available_blade_materials': BladeMaterialSerializer(available_blade_materials, many=True).data,
            }
        }, status=status.HTTP_200_OK)