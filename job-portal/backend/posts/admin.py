from django.contrib import admin
from .models import Post

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'content_preview', 'likes_count', 'comments_count', 'created_at')
    list_filter = ('author', 'created_at')
    search_fields = ('author_email', 'authorfirst_name', 'author_last_name', 'content')
    readonly_fields = ('likes_count', 'comments_count', 'created_at', 'updated_at')
    
    def content_preview(self, obj):
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'