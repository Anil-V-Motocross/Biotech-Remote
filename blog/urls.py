from django.urls import path
from .view.client_side_blog import BlogListView, BlogDetailView, blogs_by_category
from .view.admin_side_blog import blog_crud_operation, blog_category

app_name = 'blog'


urlpatterns = [
    path('blogs/', BlogListView.as_view(), name='blog-list'),
    path('blogs/<int:pk>/', BlogDetailView.as_view(), name='blog-detail'),
    path('blogs-by-category/', blogs_by_category, name='blogs-category-list'),  
    path('blogs-by-category/<slug:slug>/', blogs_by_category, name='blogs-by-category'),
    path('admin/blogs/', blog_crud_operation, name='admin-blogs-list-create'),  # List all blogs, Create new blog
    path('admin/blogs/<int:pk>/', blog_crud_operation, name='admin-blogs-detail-update-delete'), 
    path('admin/blog-categories/', blog_category, name='blog-category-list-create'),
    path('admin/blog-categories/<int:pk>/', blog_category, name='blog-category-detail-update-delete'),
]