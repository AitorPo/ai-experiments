"""
Django admin configuration for Twitter clone models.
"""

from django.contrib import admin
from .models import User, Post, Follow, Like, MediaAttachment, Hashtag, PostHashtag


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Admin configuration for User model."""
    list_display = ['username', 'display_name', 'email', 'is_verified', 'followers_count', 'posts_count', 'date_joined']
    list_filter = ['is_verified', 'is_private', 'is_active', 'date_joined']
    search_fields = ['username', 'display_name', 'email']
    readonly_fields = ['date_joined', 'last_login', 'created_at', 'updated_at']
    fieldsets = (
        ('Basic Info', {
            'fields': ('username', 'email', 'display_name', 'bio')
        }),
        ('Profile', {
            'fields': ('avatar_url', 'banner_url', 'location', 'website')
        }),
        ('Stats', {
            'fields': ('followers_count', 'following_count', 'posts_count')
        }),
        ('Settings', {
            'fields': ('is_verified', 'is_private', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('date_joined', 'last_login', 'created_at', 'updated_at')
        }),
    )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Admin configuration for Post model."""
    list_display = ['id', 'author', 'content_preview', 'post_type', 'visibility', 'likes_count', 'created_at']
    list_filter = ['post_type', 'visibility', 'is_pinned', 'is_sensitive', 'created_at']
    search_fields = ['content', 'author__username']
    readonly_fields = ['created_at', 'updated_at', 'thread_id']
    raw_id_fields = ['author', 'reply_to_post', 'reply_to_user', 'original_post']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content'


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Admin configuration for Follow model."""
    list_display = ['follower', 'followed', 'status', 'notifications_enabled', 'created_at']
    list_filter = ['status', 'notifications_enabled', 'show_retweets', 'created_at']
    search_fields = ['follower__username', 'followed__username']
    readonly_fields = ['created_at', 'updated_at']
    raw_id_fields = ['follower', 'followed']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    """Admin configuration for Like model."""
    list_display = ['user', 'post', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'post__content']
    readonly_fields = ['created_at']
    raw_id_fields = ['user', 'post']


@admin.register(MediaAttachment)
class MediaAttachmentAdmin(admin.ModelAdmin):
    """Admin configuration for MediaAttachment model."""
    list_display = ['post', 'media_type', 'url', 'created_at']
    list_filter = ['media_type', 'created_at']
    readonly_fields = ['created_at']
    raw_id_fields = ['post']


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    """Admin configuration for Hashtag model."""
    list_display = ['name', 'usage_count', 'trending_score', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(PostHashtag)
class PostHashtagAdmin(admin.ModelAdmin):
    """Admin configuration for PostHashtag model."""
    list_display = ['post', 'hashtag', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']
    raw_id_fields = ['post', 'hashtag']
