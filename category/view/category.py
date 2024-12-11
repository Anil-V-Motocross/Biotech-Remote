from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from category.models import Category
from rest_framework_simplejwt.authentication import JWTAuthentication
from account.permissions import DynamicPermission
from rest_framework import serializers

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])  
@authentication_classes([JWTAuthentication])
def category(request, pk=None):
    if request.method == 'GET' and not pk:
        required_permissions = [
            'category.view_category'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        data = {
            'categories': serializer.data
        }
        return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
    
    if request.method == 'GET' and pk:
        required_permissions = [
            'category.view_category'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if Category.objects.filter(id=pk).exists():
            category = Category.objects.get(id=pk)
            serializer = CategorySerializer(category)
            data = {
                'category': serializer.data
            }
            return Response(data={'message': 'success', 'data': data}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'POST':
        required_permissions = [
            'category.add_category'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_201_CREATED)
        return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'PATCH':
        required_permissions = [
            'category.change_category'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        category_id = request.data.get('category_id', None)
        if not category_id:
            return Response(data={'message': 'category_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Category.objects.filter(id=category_id).exists():
            category = Category.objects.get(id=category_id)
            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(data={'message': 'success', 'data': serializer.data}, status=status.HTTP_200_OK)
            return Response(data={'message': 'error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={'message': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'DELETE':
        required_permissions = [
            'category.delete_category'
        ]
        
        if not any(request.user.has_perm(perm) for perm in required_permissions):
            return Response(data={'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        category_id = request.data.get('category_id', None)
        if not category_id:
            return Response(data={'message': 'category_id is required.'}, status=status.HTTP_400_BAD_REQUEST)
        
        if Category.objects.filter(id=category_id).exists():
            category = Category.objects.get(id=category_id)
            category.delete()
            return Response(data={'message': 'success'}, status=status.HTTP_200_OK)
        return Response(data={'message': 'Category not found.'}, status=status.HTTP_404_NOT_FOUND)

    return Response({'message': 'Something went wrong.!'}, status=status.HTTP_200_OK)