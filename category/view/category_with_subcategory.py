from rest_framework import serializers
from category.models import Category, SubCategory
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission
from rest_framework import status

class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = ['id', 'name', 'is_published']

class CategorySerializer(serializers.ModelSerializer):
    subcategories = SubCategorySerializer(many=True, source='subcategory_set')

    class Meta:
        model = Category
        fields = ['id', 'name', 'subcategories']


@api_view(['GET'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def category_with_subCategory(request):
    if request.method == 'GET':  
        categories = Category.objects.prefetch_related('subcategory_set').filter(is_published=True)
        serializer = CategorySerializer(categories, many=True)
        data = {
            'categories': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    return Response({'message': 'Something went wrong.!'}, status=status.HTTP_200_OK)