from rest_framework.decorators import api_view
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from product.models import MainProduct, MainProductImage
from rest_framework import status
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission
from rest_framework.decorators import permission_classes, authentication_classes

class AddOnSerializer(serializers.ModelSerializer):
    """Serializer to return only id and name for add-ons"""
    class Meta:
        model = MainProduct
        fields = ['id', 'name']

class MainProductSerializer(serializers.ModelSerializer):
    add_ons = AddOnSerializer(many=True, read_only=True)
    class Meta:
        model = MainProduct
        fields = '__all__'

class MainProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainProductImage
        fields = '__all__'



@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def main_product(request, pk=None):
    if request.method == 'GET' and not pk:
        required_permissions = [
            'product.view_mainproduct'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        filter_params = {}
        type = request.query_params.get('type', None)
        
        if type:
            filter_params['type'] = type

        products = MainProduct.objects.filter(**filter_params).all()
        
        # products = MainProduct.objects.all()
        serializer = MainProductSerializer(products, many=True)
        data = {
            'products': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        required_permissions = [
            'product.add_mainproduct', 'product.add_mainproductimage'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)


        # Extract product data
        product_data = {
            'name': request.data.get('name'),
            'short_description': request.data.get('short_description'),
            'ribbon': request.data.get('ribbon'),
            'threshold': request.data.get('threshold'),
            'description': request.data.get('description'),
            'whats_included': request.data.get('whats_included'),
            'vedio_link': request.data.get('vedio_link'),
            'type': request.data.get('type'),
        }

        # Serialize and save product
        product_serializer = MainProductSerializer(data=product_data)
        if product_serializer.is_valid():
            product = product_serializer.save()
        else:
            return Response(product_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Handle Many-to-Many field (add_ons)
        add_on_ids = request.data.get('add_ons', [])  # Default to an empty list if not provided

        # Ensure add_ons is always a list
        if isinstance(add_on_ids, str):
            add_on_ids = add_on_ids.split(',')  # Convert comma-separated string to list

        elif isinstance(add_on_ids, int):  
            add_on_ids = [add_on_ids]  # Convert single integer to a list

        # Convert string IDs to integers (if needed)
        add_on_ids = [int(add_on_id) for add_on_id in add_on_ids]

        # Assign Many-to-Many field
        if add_on_ids:
            product.add_ons.set(add_on_ids)



        # Handle images
        images = request.FILES.getlist('photos')

        image_instances = []
        for idx, image in enumerate(images):
            image_data = {
                'product': product.id,
                'image': image
            }
            image_serializer = MainProductImageSerializer(data=image_data)
            if image_serializer.is_valid():
                saved_image = image_serializer.save()
                image_instances.append(saved_image)
            else:
                return Response(image_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = {
            'product': product_serializer.data,
        }

        return Response(data={"message": "success", "data": data}, status=status.HTTP_201_CREATED)

    # --- PATCH Method (Update) ---
    if request.method == 'PATCH' and pk:
        required_permissions = ['product.change_mainproduct']
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            product = MainProduct.objects.get(pk=pk)
        except MainProduct.DoesNotExist:
            return Response({'message': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Update product fields
        for field in ['name', 'short_description', 'ribbon', 'threshold', 'description', 'whats_included', 'vedio_link', 'type']:
            if field in request.data:
                setattr(product, field, request.data[field])

        product.save()

        # Update add_ons
        if 'add_ons' in request.data:
            add_on_ids = request.data['add_ons']
            if isinstance(add_on_ids, str):
                add_on_ids = add_on_ids.split(',')
            elif isinstance(add_on_ids, int):
                add_on_ids = [add_on_ids]

            add_on_ids = [int(add_on_id) for add_on_id in add_on_ids]
            product.add_ons.set(add_on_ids)

        # Update images
        images = request.FILES.getlist('image')
        if images:
            # MainProductImage.objects.filter(product=product).delete()  # Remove old images
            for image in images:
                MainProductImage.objects.create(product=product, image=image)

        return Response({'message': 'Product updated successfully.', 'data': MainProductSerializer(product).data}, status=status.HTTP_200_OK)

    # --- DELETE Method (Delete Product) ---
    if request.method == 'DELETE' and pk:
        required_permissions = ['product.delete_mainproduct']
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            product = MainProduct.objects.get(pk=pk)
        except MainProduct.DoesNotExist:
            return Response({'message': 'Product not found.'}, status=status.HTTP_404_NOT_FOUND)

        product.delete()  # Automatically deletes related images due to ForeignKey CASCADE
        return Response({'message': 'Product deleted successfully.'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'message': 'Invalid request method or missing ID.'}, status=status.HTTP_400_BAD_REQUEST)    
