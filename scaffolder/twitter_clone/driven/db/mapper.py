"""
Mappers for converting between domain entities and Django models.
"""

from typing import Dict, Any
from datetime import datetime

from domain.entities.user import UserEntity
from domain.entities.post import PostEntity, PostType, PostVisibility
from domain.entities.follow import FollowEntity, FollowStatus
from domain.entities.like import LikeEntity
from .models import User, Post, Follow, Like


class UserDBMapper:
    """Maps between UserEntity and User Django model."""
    
    def dbo_to_entity(self, dbo: User) -> UserEntity:
        """Convert Django model to domain entity."""
        return UserEntity(
            id=dbo.id,
            username=dbo.username,
            email=dbo.email,
            display_name=dbo.display_name,
            bio=dbo.bio,
            avatar_url=dbo.avatar_url,
            banner_url=dbo.banner_url,
            location=dbo.location,
            website=dbo.website,
            followers_count=dbo.followers_count,
            following_count=dbo.following_count,
            posts_count=dbo.posts_count,
            is_verified=dbo.is_verified,
            is_private=dbo.is_private,
            is_active=dbo.is_active,
            date_joined=dbo.date_joined,
            last_login=dbo.last_login,
            created_at=dbo.created_at,
            updated_at=dbo.updated_at,
        )
    
    def entity_to_dbo_data(self, entity: UserEntity) -> Dict[str, Any]:
        """Convert domain entity to Django model data."""
        return {
            'username': entity.username,
            'email': entity.email,
            'display_name': entity.display_name,
            'bio': entity.bio,
            'avatar_url': entity.avatar_url,
            'banner_url': entity.banner_url,
            'location': entity.location,
            'website': entity.website,
            'followers_count': entity.followers_count,
            'following_count': entity.following_count,
            'posts_count': entity.posts_count,
            'is_verified': entity.is_verified,
            'is_private': entity.is_private,
            'is_active': entity.is_active,
        }


class PostDBMapper:
    """Maps between PostEntity and Post Django model."""
    
    def dbo_to_entity(self, dbo: Post) -> PostEntity:
        """Convert Django model to domain entity."""
        return PostEntity(
            id=dbo.id,
            author_id=dbo.author_id,
            content=dbo.content,
            post_type=PostType(dbo.post_type),
            visibility=PostVisibility(dbo.visibility),
            reply_to_post_id=dbo.reply_to_post_id,
            reply_to_user_id=dbo.reply_to_user_id,
            thread_id=dbo.thread_id,
            original_post_id=dbo.original_post_id,
            quote_comment=dbo.quote_comment,
            media_attachments=[],  # Would be populated separately
            likes_count=dbo.likes_count,
            retweets_count=dbo.retweets_count,
            replies_count=dbo.replies_count,
            quote_tweets_count=dbo.quote_tweets_count,
            is_pinned=dbo.is_pinned,
            is_sensitive=dbo.is_sensitive,
            language=dbo.language,
            created_at=dbo.created_at,
            updated_at=dbo.updated_at,
        )
    
    def entity_to_dbo_data(self, entity: PostEntity) -> Dict[str, Any]:
        """Convert domain entity to Django model data."""
        return {
            'author_id': entity.author_id,
            'content': entity.content,
            'post_type': entity.post_type.value,
            'visibility': entity.visibility.value,
            'reply_to_post_id': entity.reply_to_post_id,
            'reply_to_user_id': entity.reply_to_user_id,
            'thread_id': entity.thread_id,
            'original_post_id': entity.original_post_id,
            'quote_comment': entity.quote_comment,
            'likes_count': entity.likes_count,
            'retweets_count': entity.retweets_count,
            'replies_count': entity.replies_count,
            'quote_tweets_count': entity.quote_tweets_count,
            'is_pinned': entity.is_pinned,
            'is_sensitive': entity.is_sensitive,
            'language': entity.language,
        }


class FollowDBMapper:
    """Maps between FollowEntity and Follow Django model."""
    
    def dbo_to_entity(self, dbo: Follow) -> FollowEntity:
        """Convert Django model to domain entity."""
        return FollowEntity(
            id=dbo.id,
            follower_id=dbo.follower_id,
            followed_id=dbo.followed_id,
            status=FollowStatus(dbo.status),
            notifications_enabled=dbo.notifications_enabled,
            show_retweets=dbo.show_retweets,
            created_at=dbo.created_at,
            updated_at=dbo.updated_at,
        )
    
    def entity_to_dbo_data(self, entity: FollowEntity) -> Dict[str, Any]:
        """Convert domain entity to Django model data."""
        return {
            'follower_id': entity.follower_id,
            'followed_id': entity.followed_id,
            'status': entity.status.value,
            'notifications_enabled': entity.notifications_enabled,
            'show_retweets': entity.show_retweets,
        }


class LikeDBMapper:
    """Maps between LikeEntity and Like Django model."""
    
    def dbo_to_entity(self, dbo: Like) -> LikeEntity:
        """Convert Django model to domain entity."""
        return LikeEntity(
            id=dbo.id,
            user_id=dbo.user_id,
            post_id=dbo.post_id,
            created_at=dbo.created_at,
        )
    
    def entity_to_dbo_data(self, entity: LikeEntity) -> Dict[str, Any]:
        """Convert domain entity to Django model data."""
        return {
            'user_id': entity.user_id,
            'post_id': entity.post_id,
        }
