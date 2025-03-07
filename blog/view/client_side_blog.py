
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.generics import ListAPIView, RetrieveAPIView
from blog.models import Blog, BlogCategory
from blog.serializers import BlogSerializer,BlogCategorySerializer


class BlogListView(ListAPIView):
    serializer_class = BlogSerializer

    def get(self, request, *args, **kwargs):
        """
        Custom GET method for listing all published blogs.
        """
        try:
            blogs = Blog.objects.filter(status="published", is_visible=True).order_by('-published_at')

            if not blogs.exists():
                return Response(
                    {"message": "No blogs available."}, 
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = self.get_serializer(blogs, many=True, context={"list_view": True})
            return Response(
                data={'message': 'Blogs retrieved successfully', 'data': {"blogs":serializer.data}}, 
                status=status.HTTP_200_OK
            )

        
        except Exception as e:
            return Response(
                data={'message': 'An error occurred while retrieving blogs', 'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class BlogDetailView(RetrieveAPIView):
    serializer_class = BlogSerializer

    def get(self, request, pk, *args, **kwargs):
        """
        Custom GET method to retrieve a single blog by ID.
        """
        try:
            blog = Blog.objects.get(id=pk, status="published", is_visible=True)

            serializer = self.get_serializer(blog, context={"list_view": False})
            return Response(
                data={'message': 'Blog retrieved successfully', 'data': {"blog_details":serializer.data}}, 
                status=status.HTTP_200_OK
            )
        
        except Blog.DoesNotExist:
            return Response(
                data={'message': 'Blog not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(
                data={'message': 'An error occurred while retrieving the blog', 'error': str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


@api_view(['GET'])
def blogs_by_category(request, slug=None):
    """
    Retrieve categories or blogs under a specific category.
    """
    try:
        if not slug:
            # Return all categories if no slug is provided
            categories = BlogCategory.objects.filter(is_publish=True)
            serializer = BlogCategorySerializer(categories, many=True)
            return Response(
                data={'message': 'Categories retrieved successfully', 'data': {"blog_categories":serializer.data}}, 
                status=status.HTTP_200_OK
            )

        # Fetch category by slug
        category = BlogCategory.objects.get(slug=slug)
        blogs = Blog.objects.filter(category=category, is_visible=True).order_by('-published_at')

        if not blogs.exists():
            return Response(
                data={'message': 'No blogs available in this category'}, 
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BlogSerializer(blogs, many=True, context={"list_view": True})
        return Response(
            data={'message': 'Blogs retrieved successfully', 'data': {"blogs_by_category":serializer.data}}, 
            status=status.HTTP_200_OK
        )

    except BlogCategory.DoesNotExist:
        return Response(
            data={'message': 'Category not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )

    except Exception as e:
        return Response(
            data={'message': 'An error occurred while retrieving blogs', 'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


