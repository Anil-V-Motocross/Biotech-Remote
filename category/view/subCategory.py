from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from category.models import SubCategory
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission
from rest_framework import serializers


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = '__all__'

@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def subCategory(request, pk=None):
    if request.method == 'GET' and not pk:
        required_permissions = [
            'category.view_subcategory'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        subCategories = SubCategory.objects.all()
        serializer = SubCategorySerializer(subCategories, many=True)
        data = {
            'subCategories': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    if request.method == 'GET' and pk:
        required_permissions = [
            'category.view_subcategory'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if SubCategory.objects.filter(id=pk).exists():
            subCategory = SubCategory.objects.get(id=pk)
            serializer = SubCategorySerializer(subCategory)
            data = {
                'subCategory': serializer.data
            }
            return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
        return Response(data={'message': 'SubCategory not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        required_permissions = [
            'category.add_subcategory'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = SubCategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'PATCH':
        required_permissions = [
            'category.change_subcategory'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        subCategory_id = request.data.get('subCategory_id')

        if not subCategory_id:
            return Response(data={'message': 'SubCategory id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if SubCategory.objects.filter(id=subCategory_id).exists():
            subCategory = SubCategory.objects.get(id=subCategory_id)
            serializer = SubCategorySerializer(subCategory, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': 'SubCategory not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'DELETE':
        required_permissions = [
            'category.delete_subcategory'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        subCategory_id = request.data.get('subCategory_id')

        if not subCategory_id:
            return Response(data={'message': 'SubCategory id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if SubCategory.objects.filter(id=subCategory_id).exists():
            subCategory = SubCategory.objects.get(id=subCategory_id)
            subCategory.delete()
            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'SubCategory not found.'}, status=status.HTTP_404_NOT_FOUND)

    return Response(data={'message': 'Something went wrong.!'}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def category_wise_subCategory(request, pk=None):
    if request.method == 'GET':
        subCategorys = SubCategory.objects.filter(category_id=pk)
        serializer = SubCategorySerializer(subCategorys, many=True)
        data = {
            'subCategorys': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    return Response({'message': 'Something went wrong.!'}, status=status.HTTP_200_OK)
    