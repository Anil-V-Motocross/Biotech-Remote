from rest_framework import serializers 
from .models import Blog, BlogCategory
from rest_framework.response import Response
from django.utils.timezone import now

class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug']

class BlogCategoryAdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ['id', 'name', 'slug', 'is_publish']

class BlogAdminSerializer(serializers.ModelSerializer):
    category = BlogCategorySerializer(read_only=True)  # Nested category details
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=BlogCategory.objects.all(), write_only=True
    )  # Accepts category ID when creating/updating
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    published_at = serializers.DateTimeField(read_only=True)
    
    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'category', 'category_id', 
            'image', 'status', 'tags', 'author', 'is_visible', 
            'created_at', 'updated_at', 'published_at'
        ]

    def create(self, validated_data):
        """Override create method to correctly handle category_id"""
        category = validated_data.pop('category_id')  # Extract category ID
        blog = Blog.objects.create(category=category, **validated_data)  # Pass category instance
        return blog
    
    def update(self, instance, validated_data):
        """
        Automatically update `published_at` when status changes to 'published'
        """
        status_before = instance.status
        status_after = validated_data.get("status", instance.status)

        if status_before != "published" and status_after == "published":
            validated_data["published_at"] = now()

        category_id = validated_data.pop('category_id', None)
        if isinstance(category_id, BlogCategory):  
            category_id = category_id.id 

        if category_id:
            try:
                category_instance = BlogCategory.objects.get(id=category_id)  # Assign correctly
                instance.category = category_instance
            except BlogCategory.DoesNotExist:
                raise serializers.ValidationError({'category_id': 'Invalid category ID.'})

        return super().update(instance, validated_data)

class BlogSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()  # Show category name instead of full details
    excerpt = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = ['id', 'title', 'slug', 'excerpt', 'content', 'category', 'image', 'author', 'published_at']

    def get_excerpt(self, obj):
        """
        Return an excerpt only when used in list view.
        """
        if self.context.get("list_view", False):
            return obj.content[:150] + "..." if obj.content else ""  # First 150 chars
        return None  # Don't include in detail view

    def to_representation(self, instance):
        """
        Customize output based on the context.
        If it's a list view, exclude `content`, otherwise exclude `excerpt`.
        """
        data = super().to_representation(instance)
        if self.context.get("list_view", False):
            data.pop("content", None)  # Remove `content` for list view
        else:
            data.pop("excerpt", None)  # Remove `excerpt` for detail view
        return data
