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

# @api_view(['GET'])
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
            'product': serializer.data,
            'product_planter_sizes': pot_sizes,
            'product_colors': pot_colors,
            'tool_sizes': tool_sizes,
            'product_colors': tool_colors,
            'product_rating': product_rating,
            'product_reviews': product_reviews,
        }
        
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    return Response(data={'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)



# def filter_inventory(request, pk):
#     if not InventoryItem.objects.filter(id=pk).exists():
#         return Response(data={'message': 'Inventory item does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

#     current_item = InventoryItem.objects.get(id=pk)
#     item_type = current_item.category
#     filter_params = {'inventory_item_id': current_item.id, 'visible_online': True}  # Fixed

#     if item_type == 'pot':
#         size_id = request.query_params.get('size_id', None)
#         litre = request.query_params.get('litre', None)
#         color_id = request.query_params.get('color_id', None)

#         if size_id and litre:
#             return Response(data={'message': 'Select either size or litre, not both.'}, status=status.HTTP_400_BAD_REQUEST)

#         if size_id:
#             filter_params['size_id'] = size_id
#         if litre:
#             filter_params['litre'] = litre
#         if color_id:
#             filter_params['color_id'] = color_id

#         pot_variants = PotVariant.objects.filter(**filter_params)
#         if not pot_variants.exists():
#             return Response(data={'message': 'No matching pot variant found.'}, status=status.HTTP_400_BAD_REQUEST)

#         selected_variant = pot_variants.first()

#         available_sizes = Size.objects.none()
#         available_litres = []
        
#         if size_id:
#             available_colors = Color.objects.filter(
#                 id__in=PotVariant.objects.filter(inventory_item_id=current_item.id, size_id=size_id)  # Fixed
#                 .values_list('color_id', flat=True)
#                 .distinct()
#             )
#         elif litre:
#             available_colors = Color.objects.filter(
#                 id__in=PotVariant.objects.filter(inventory_item_id=current_item.id, litre=litre)  # Fixed
#                 .values_list('color_id', flat=True)
#                 .distinct()
#             )
#         else:
#             available_colors = Color.objects.filter(
#                 id__in=PotVariant.objects.filter(inventory_item_id=current_item.id)  # Fixed
#                 .values_list('color_id', flat=True)
#                 .distinct()
#             )

#         if not litre:
#             available_sizes = Size.objects.filter(
#                 id__in=PotVariant.objects.filter(inventory_item_id=current_item.id)  # Fixed
#                 .values_list('size_id', flat=True)
#                 .distinct()
#             )

#         if not size_id:
#             available_litres = list(
#                 PotVariant.objects.filter(inventory_item_id=current_item.id)  # Fixed
#                 .values_list('litre', flat=True)
#                 .distinct()
#             )

#         return Response(data={
#             'message': 'success',
#             'data': {
#                 'product_type': item_type,
#                 'product': FilteredInventorySerializer(current_item, context={'request': request, 'selected_variant': selected_variant}).data,
#                 'product_planter_sizes': SizeSerializer(available_sizes, many=True).data,
#                 'available_litres': available_litres,
#                 'product_colors': ColorSerializer(available_colors, many=True).data,
#             }
#         }, status=status.HTTP_200_OK)

    # elif item_type == 'tool':
    #     size_id = request.query_params.get('size_id', None)
    #     color_id = request.query_params.get('color_id', None)

    #     if size_id:
    #         filter_params['size_id'] = size_id
    #     if color_id:
    #         filter_params['color_id'] = color_id

    #     tool_variants = ToolVariant.objects.filter(**filter_params)
    #     if not tool_variants.exists():
    #         return Response(data={'message': 'No matching tool variant found.'}, status=status.HTTP_400_BAD_REQUEST)

    #     selected_variant = tool_variants.first()

    #     available_sizes = Size.objects.none()
    #     available_colors = Color.objects.none()

    #     if size_id:
    #         available_colors = Color.objects.filter(
    #             id__in=ToolVariant.objects.filter(inventory_item_id=current_item.id, size_id=size_id)  # Fixed
    #             .values_list('color_id', flat=True)
    #             .distinct()
    #         )
    #     else:
    #         available_sizes = Size.objects.filter(
    #             id__in=ToolVariant.objects.filter(inventory_item_id=current_item.id)  # Fixed
    #             .values_list('size_id', flat=True)
    #             .distinct()
    #         )

    #     return Response(data={
    #         'message': 'success',
    #         'data': {
    #             'product_type': item_type,
    #             'product': FilteredInventorySerializer(current_item, context={'request': request, 'selected_variant': selected_variant}).data,
    #             'product_sizes': SizeSerializer(available_sizes, many=True).data,
    #             'product_colors': ColorSerializer(available_colors, many=True).data,
    #         }
    #     }, status=status.HTTP_200_OK)

def filter_inventory(request, pk):
    if not InventoryItem.objects.filter(id=pk).exists():
        return Response(data={'message': 'Inventory item does not exist.'}, status=status.HTTP_400_BAD_REQUEST)

    current_item = InventoryItem.objects.get(id=pk)
    item_type = current_item.category
    filter_params = {'inventory_item_id': current_item.id, 'visible_online': True}

    selected_variant = None
    available_sizes = []
    available_litres = []
    available_colors = []

    if item_type == 'pot':
        size_id = request.query_params.get('size_id', None)
        litre = request.query_params.get('litre', None)
        color_id = request.query_params.get('color_id', None)

        # Prevent selecting both size and litre
        if size_id and litre:
            return Response(data={'message': 'Select either size or litre, not both.'}, status=status.HTTP_400_BAD_REQUEST)

        # If only size_id is provided
        if size_id and not color_id:
            available_sizes = list(
                PotVariant.objects.filter(inventory_item_id=current_item.id)
                .values_list('size_id', flat=True)
                .distinct()
            )

            available_colors = Color.objects.filter(
                id__in=PotVariant.objects.filter(inventory_item_id=current_item.id, size_id=size_id)
                .values_list('color_id', flat=True)
                .distinct()
            )

            available_litres = []  # No litres when size_id is provided

        # If only litre is provided
        elif litre and not color_id:
            available_litres = list(
                PotVariant.objects.filter(inventory_item_id=current_item.id)
                .values_list('litre', flat=True)
                .distinct()
            )

            available_colors = Color.objects.filter(
                id__in=PotVariant.objects.filter(inventory_item_id=current_item.id, litre=litre)
                .values_list('color_id', flat=True)
                .distinct()
            )

            available_sizes = []  # No sizes when litre is provided

        # If both size_id and color_id are provided, return variant or error
        elif size_id and color_id:
            selected_variant = PotVariant.objects.filter(inventory_item_id=current_item.id, size_id=size_id, color_id=color_id).first()
            if not selected_variant:
                return Response(data={'message': 'This combination of size and color is not available.'}, status=status.HTTP_400_BAD_REQUEST)

            available_sizes = list(
                PotVariant.objects.filter(inventory_item_id=current_item.id)
                .values_list('size_id', flat=True)
                .distinct()
            )

            available_colors = Color.objects.filter(
                id__in=PotVariant.objects.filter(inventory_item_id=current_item.id, size_id=size_id)
                .values_list('color_id', flat=True)
                .distinct()
            )

            available_litres = []  # When size_id is selected, litres should be empty

        # If both litre and color_id are provided, return variant or error
        elif litre and color_id:
            selected_variant = PotVariant.objects.filter(inventory_item_id=current_item.id, litre=litre, color_id=color_id).first()
            if not selected_variant:
                return Response(data={'message': 'This combination of litre and color is not available.'}, status=status.HTTP_400_BAD_REQUEST)

            available_litres = list(
                PotVariant.objects.filter(inventory_item_id=current_item.id)
                .values_list('litre', flat=True)
                .distinct()
            )

            available_colors = Color.objects.filter(
                id__in=PotVariant.objects.filter(inventory_item_id=current_item.id, litre=litre)
                .values_list('color_id', flat=True)
                .distinct()
            )

            available_sizes = []  # When litre is selected, sizes should be empty

        # If only color_id is provided without size_id or litre, return an error
        elif color_id:
            return Response(data={'message': 'Provide either size_id or litre with color_id.'}, status=status.HTTP_400_BAD_REQUEST)

        # Final Response with all necessary data
        return Response(data={
            'message': 'success',
            'data': {
                'product_type': item_type,
                'variant_id': selected_variant.id if selected_variant else None,
                'product': FilteredInventorySerializer(current_item, context={'request': request, 'selected_variant': selected_variant}).data,
                'product_sizes': SizeSerializer(Size.objects.filter(id__in=available_sizes), many=True).data,
                'available_litres': available_litres,
                'product_colors': ColorSerializer(available_colors, many=True).data,
            }
        }, status=status.HTTP_200_OK)

    elif item_type == 'tool':
        size_id = request.query_params.get('size_id', None)
        color_id = request.query_params.get('color_id', None)

        # Validate: Must provide both size_id and color_id
        if (size_id and not color_id) or (color_id and not size_id):
            return Response(data={'message': 'Provide both size_id and color_id for tools.'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # Ensure that the requested tool variant exists
        exists = ToolVariant.objects.filter(inventory_item_id=current_item.id, size_id=size_id, color_id=color_id).exists()
        if not exists:
            return Response(data={'message': 'This combination of size and color is not available.'}, status=status.HTTP_400_BAD_REQUEST)

        # Fetch matching tool variant
        filter_params.update({'size_id': size_id, 'color_id': color_id})
        tool_variants = ToolVariant.objects.filter(**filter_params)
        if not tool_variants.exists():
            return Response(data={'message': 'No matching tool variant found.'}, status=status.HTTP_400_BAD_REQUEST)

        selected_variant = tool_variants.first()

        # Fetch available options
        available_sizes = Size.objects.filter(
            id__in=ToolVariant.objects.filter(inventory_item_id=current_item.id)
            .values_list('size_id', flat=True)
            .distinct()
        )

        available_colors = Color.objects.filter(
            id__in=ToolVariant.objects.filter(inventory_item_id=current_item.id)
            .values_list('color_id', flat=True)
            .distinct()
        )

        return Response(data={
            'message': 'success',
            'data': {
                'product_type': item_type,
                'variant_id': selected_variant.id,  # Ensure the correct tool variant ID is returned
                'product': FilteredInventorySerializer(current_item, context={'request': request, 'selected_variant': selected_variant}).data,
                'product_sizes': SizeSerializer(available_sizes, many=True).data,
                'product_colors': ColorSerializer(available_colors, many=True).data,
            }
        }, status=status.HTTP_200_OK)

    return Response(data={'message': 'Invalid item type.'}, status=status.HTTP_400_BAD_REQUEST)
