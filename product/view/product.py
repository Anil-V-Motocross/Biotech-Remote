from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from product.models import Product
from account.permissions import DynamicPermission
from rest_framework import serializers
from django.core.files.base import ContentFile
import json

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'


@api_view(['POST'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def product(request):
    if request.method == 'POST':
        required_permissions = [
            'product.add_product'
        ]

        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        products_data = request.data.get('data')
        products_data = json.loads(products_data)
        images = request.FILES.getlist('file')

        if len(products_data) != len(images):
            return Response(
                {'message': 'Each product must have a corresponding image.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        saved_products = []
        errors = []

        for index, product_data in enumerate(products_data):
            try:
                # Validate and ensure the MainProduct exists
                main_product_id = product_data.get('product_id')
                if not main_product_id:
                    errors.append({'product_data': product_data, 'error': 'Missing product_id.'})
                    continue

                serializer = ProductSerializer(data=product_data)

                if serializer.is_valid():
                    product = serializer.save()

                    # Attach image to the product
                    image = images[index]
                    product.image.save(image.name, ContentFile(image.read()), save=True)

                    saved_products.append(product)
                else:
                    errors.append({
                        'product_data': product_data,
                        'errors': serializer.errors
                    })
            except json.JSONDecodeError:
                errors.append({'product_data': product_data, 'error': 'Invalid JSON format'})
            except Exception as e:
                errors.append({'product_data': product_data, 'error': str(e)})

        if errors:
            return Response(
                {'message': 'Some products could not be saved.', 'errors': errors}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        return Response(
            {'message': 'Products added successfully.', 'saved_products': [p.id for p in saved_products]}, 
            status=status.HTTP_201_CREATED
        )

    return Response(data={'message': 'Invalid request method.'}, status=status.HTTP_400_BAD_REQUEST)
