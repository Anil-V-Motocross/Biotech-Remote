from django.db.utils import IntegrityError
from django.utils.text import slugify
from django.utils.timezone import now
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from blog.models import Blog, BlogCategory
from blog.serializers import BlogAdminSerializer, BlogCategoryAdminSerializer
from account.permissions import DynamicPermission

@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def blog_crud_operation(request, pk=None):
    # List all blogs
    if request.method == 'GET' and not pk:
        if not request.user.has_perm('BlogMain.view_blog'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        blogs = Blog.objects.all()
        serializer = BlogAdminSerializer(blogs, many=True)
        return Response({'message': 'Blogs retrieved successfully', 'data': {'blogs': serializer.data}}, status=status.HTTP_200_OK)

    # Retrieve a single blog by ID
    if request.method == 'GET' and pk:
        if not request.user.has_perm('BlogMain.view_blog'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            blog = Blog.objects.get(id=pk)
            serializer = BlogAdminSerializer(blog)
            return Response({'message': 'Blog retrieved successfully', 'data': {'blog': serializer.data}}, status=status.HTTP_200_OK)
        except Blog.DoesNotExist:
            return Response({'message': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)

    # Create a new blog
    if request.method == 'POST':
        if not request.user.has_perm('BlogMain.add_blog'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        serializer = BlogAdminSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response({'message': 'Blog created successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'message': 'Slug already exists, please enter a new slug'}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'message': 'Validation error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    # Update a blog
    if request.method == 'PATCH':
        print("request data ----:", request.data)
        if not request.user.has_perm('BlogMain.change_blog'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        mutable_data = request.data.copy()
        # blog_id = mutable_data.get('pk')

        if not pk:
            return Response({'message': 'Blog ID (pk) is required in the URL'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            blog = Blog.objects.get(id=pk)

            if 'title' in mutable_data:
                mutable_data['slug'] = slugify(mutable_data['title'])  # Auto-generate slug

            serializer = BlogAdminSerializer(blog, data=mutable_data, partial=True)

            if serializer.is_valid():
                serializer.save()
                return Response({'message': 'Blog updated successfully', 'data': serializer.data}, status=status.HTTP_200_OK)
            return Response({'message': 'Validation error', 'errors': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Blog.DoesNotExist:
            return Response({'message': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)

    # Delete a blog
    if request.method == 'DELETE':
        if not request.user.has_perm('BlogMain.delete_blog'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

        try:
            blog = Blog.objects.get(id=pk)
            blog.delete()
            return Response({'message': 'Blog deleted successfully'}, status=status.HTTP_200_OK)
        except Blog.DoesNotExist:
            return Response({'message': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)




# ************ Blog Category ***********
@api_view(['GET', 'POST', 'PATCH', 'DELETE'])
@permission_classes([IsAuthenticated, DynamicPermission])
@authentication_classes([JWTAuthentication])
def blog_category(request, pk=None):
    """Handles CRUD operations for BlogCategory."""

    if request.method == 'GET':
        if not request.user.has_perm('BlogMain.add_blogcategory'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        if pk:
            try:
                category = BlogCategory.objects.get(id=pk)
                serializer = BlogCategoryAdminSerializer(category)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except BlogCategory.DoesNotExist:
                return Response({'message': 'No category found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            categories = BlogCategory.objects.all()
            serializer = BlogCategoryAdminSerializer(categories, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
    
    if request.method == 'POST':
        if not request.user.has_perm('BlogMain.add_blogcategory'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = BlogCategoryAdminSerializer(data=request.data)
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError:
                return Response({'message': 'Slug already exists, please enter a new slug'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'PATCH':
        if not request.user.has_perm('BlogMain.change_blogcategory'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        if not pk:
            return Response({'message': 'Category ID (pk) is required in the URL'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            category = BlogCategory.objects.get(pk=pk)
            mutable_data = request.data.copy()
            if 'name' in mutable_data:
                mutable_data['slug'] = slugify(mutable_data['name'])
            
            serializer = BlogCategoryAdminSerializer(category, data=mutable_data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except BlogCategory.DoesNotExist:
            return Response({'message': 'No category found'}, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'DELETE':
        if not request.user.has_perm('BlogMain.delete_blogcategory'):
            return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            category = BlogCategory.objects.get(pk=pk)
            category.delete()
            return Response({'message': 'Category deleted successfully'}, status=status.HTTP_200_OK)
        except BlogCategory.DoesNotExist:
            return Response({'message': 'No category found'}, status=status.HTTP_404_NOT_FOUND)
    
    return Response({'message': 'Invalid request'}, status=status.HTTP_400_BAD_REQUEST)