from django.db import models
from django.utils.text import slugify
from django.utils.timezone import now
from ckeditor.fields import RichTextField  # Import CKEditor for rich text content

class BlogCategory(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True, blank=True)
    is_publish = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super(BlogCategory, self).save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Blog(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]

    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    author = models.CharField(max_length=100, null=True, blank=True)
    category = models.ForeignKey(BlogCategory, related_name='blogs', on_delete=models.CASCADE, null=True, blank=True)
    excerpt = models.TextField(null=True, blank=True)  # Short summary
    content = RichTextField()  # Rich text field for long content with formatting
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    is_visible = models.BooleanField(default=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')  # Blog post status
    tags = models.CharField(max_length=255, null=True, blank=True)  # Comma-separated tags
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Auto-updated on save
    published_at = models.DateTimeField(null=True, blank=True)  # When the blog was published

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            
        # If status is changed to "published" and published_at is not set, store the publish time
        if self.status == 'published' and not self.published_at:
            self.published_at = now()

        super(Blog, self).save(*args, **kwargs)

    def __str__(self):
        return self.title    