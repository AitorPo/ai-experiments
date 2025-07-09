"""
Database adapters implementing repository ports for Twitter clone.
"""

from typing import List, Optional
from django.contrib.auth.hashers import make_password, check_password
from django.db.models import Q, F
from django.db import models

from application.ports.driven.user_repository_port import UserRepositoryPort
from application.ports.driven.post_repository_port import PostRepositoryPort
from application.ports.driven.follow_repository_port import FollowRepositoryPort
from application.ports.driven.like_repository_port import LikeRepositoryPort
from domain.entities.user import UserEntity
from domain.entities.post import PostEntity
from domain.entities.follow import FollowEntity
from domain.entities.like import LikeEntity
from .models import User, Post, Follow, Like
from .mapper import UserDBMapper, PostDBMapper, FollowDBMapper, LikeDBMapper


class UserRepositoryAdapter(UserRepositoryPort):
    """Repository adapter for User operations."""
    
    def __init__(self):
        self.mapper = UserDBMapper()
    
    async def create_user(self, user: UserEntity, password: str) -> UserEntity:
        """Create a new user with hashed password."""
        user_data = self.mapper.entity_to_dbo_data(user)
        user_data['password'] = make_password(password)
        
        dbo = await User.objects.acreate(**user_data)
        return self.mapper.dbo_to_entity(dbo)
    
    async def find_by_id(self, user_id: int) -> Optional[UserEntity]:
        """Find a user by ID."""
        try:
            dbo = await User.objects.aget(id=user_id)
            return self.mapper.dbo_to_entity(dbo)
        except User.DoesNotExist:
            return None
    
    async def find_by_username(self, username: str) -> Optional[UserEntity]:
        """Find a user by username."""
        try:
            dbo = await User.objects.aget(username=username)
            return self.mapper.dbo_to_entity(dbo)
        except User.DoesNotExist:
            return None
    
    async def find_by_email(self, email: str) -> Optional[UserEntity]:
        """Find a user by email."""
        try:
            dbo = await User.objects.aget(email=email)
            return self.mapper.dbo_to_entity(dbo)
        except User.DoesNotExist:
            return None
    
    async def update_user(self, user_id: int, updates: dict) -> Optional[UserEntity]:
        """Update an existing user."""
        try:
            await User.objects.filter(id=user_id).aupdate(**updates)
            dbo = await User.objects.aget(id=user_id)
            return self.mapper.dbo_to_entity(dbo)
        except User.DoesNotExist:
            return None
    
    async def search_users(self, query: str, limit: int) -> List[UserEntity]:
        """Search users by username or display name."""
        dbos = User.objects.filter(
            Q(username__icontains=query) | Q(display_name__icontains=query)
        ).order_by('username')[:limit]
        
        return [self.mapper.dbo_to_entity(dbo) async for dbo in dbos]
    
    async def get_followers_count(self, user_id: int) -> int:
        """Get the number of followers for a user."""
        try:
            user = await User.objects.aget(id=user_id)
            return user.followers_count
        except User.DoesNotExist:
            return 0
    
    async def get_following_count(self, user_id: int) -> int:
        """Get the number of users being followed."""
        try:
            user = await User.objects.aget(id=user_id)
            return user.following_count
        except User.DoesNotExist:
            return 0
    
    async def increment_posts_count(self, user_id: int, increment: int = 1) -> bool:
        """Increment the posts count for a user."""
        try:
            await User.objects.filter(id=user_id).aupdate(
                posts_count=F('posts_count') + increment
            )
            return True
        except:
            return False
    
    async def increment_followers_count(self, user_id: int, increment: int = 1) -> bool:
        """Increment the followers count for a user."""
        try:
            await User.objects.filter(id=user_id).aupdate(
                followers_count=F('followers_count') + increment
            )
            return True
        except:
            return False
    
    async def increment_following_count(self, user_id: int, increment: int = 1) -> bool:
        """Increment the following count for a user."""
        try:
            await User.objects.filter(id=user_id).aupdate(
                following_count=F('following_count') + increment
            )
            return True
        except:
            return False
    
    async def verify_password(self, user_id: int, password: str) -> bool:
        """Verify user password."""
        try:
            user = await User.objects.aget(id=user_id)
            return check_password(password, user.password)
        except User.DoesNotExist:
            return False


class PostRepositoryAdapter(PostRepositoryPort):
    """Repository adapter for Post operations."""
    
    def __init__(self):
        self.mapper = PostDBMapper()
    
    async def save(self, post: PostEntity) -> PostEntity:
        """Save a post to the database."""
        post_data = self.mapper.entity_to_dbo_data(post)
        dbo = await Post.objects.acreate(**post_data)
        return self.mapper.dbo_to_entity(dbo)
    
    async def find_by_id(self, post_id: int) -> Optional[PostEntity]:
        """Find a post by ID."""
        try:
            dbo = await Post.objects.select_related('author').aget(id=post_id)
            return self.mapper.dbo_to_entity(dbo)
        except Post.DoesNotExist:
            return None
    
    async def find_by_author(self, author_id: int, limit: int, offset: int = 0) -> List[PostEntity]:
        """Find all posts by a specific author."""
        dbos = Post.objects.filter(author_id=author_id).select_related('author').order_by('-created_at')[offset:offset+limit]
        return [self.mapper.dbo_to_entity(dbo) async for dbo in dbos]
    
    async def find_replies(self, post_id: int, limit: int) -> List[PostEntity]:
        """Find replies to a specific post."""
        dbos = Post.objects.filter(reply_to_post_id=post_id).select_related('author').order_by('created_at')[:limit]
        return [self.mapper.dbo_to_entity(dbo) async for dbo in dbos]
    
    async def find_user_retweet(self, user_id: int, original_post_id: int) -> Optional[PostEntity]:
        """Find if user has retweeted a specific post."""
        try:
            dbo = await Post.objects.aget(
                author_id=user_id,
                original_post_id=original_post_id,
                post_type=Post.PostType.RETWEET
            )
            return self.mapper.dbo_to_entity(dbo)
        except Post.DoesNotExist:
            return None
    
    async def get_timeline_posts(self, user_id: int, limit: int, offset: int = 0) -> List[PostEntity]:
        """Get timeline posts for a user (posts from followed users)."""
        # This would join with Follow table in a real implementation
        dbos = Post.objects.filter(
            author__followers_set__follower_id=user_id,
            author__followers_set__status=Follow.FollowStatus.ACTIVE
        ).select_related('author').order_by('-created_at')[offset:offset+limit]
        return [self.mapper.dbo_to_entity(dbo) async for dbo in dbos]
    
    async def search_posts(self, query: str, limit: int) -> List[PostEntity]:
        """Search posts by content."""
        dbos = Post.objects.filter(content__icontains=query).select_related('author').order_by('-created_at')[:limit]
        return [self.mapper.dbo_to_entity(dbo) async for dbo in dbos]
    
    async def delete_by_id(self, post_id: int) -> bool:
        """Delete a post by ID."""
        try:
            await Post.objects.filter(id=post_id).adelete()
            return True
        except:
            return False
    
    async def increment_likes_count(self, post_id: int, increment: int = 1) -> bool:
        """Increment the likes count for a post."""
        try:
            await Post.objects.filter(id=post_id).aupdate(
                likes_count=F('likes_count') + increment
            )
            return True
        except:
            return False
    
    async def increment_retweets_count(self, post_id: int, increment: int = 1) -> bool:
        """Increment the retweets count for a post."""
        try:
            await Post.objects.filter(id=post_id).aupdate(
                retweets_count=F('retweets_count') + increment
            )
            return True
        except:
            return False
    
    async def increment_replies_count(self, post_id: int, increment: int = 1) -> bool:
        """Increment the replies count for a post."""
        try:
            await Post.objects.filter(id=post_id).aupdate(
                replies_count=F('replies_count') + increment
            )
            return True
        except:
            return False
    
    async def increment_quote_tweets_count(self, post_id: int, increment: int = 1) -> bool:
        """Increment the quote tweets count for a post."""
        try:
            await Post.objects.filter(id=post_id).aupdate(
                quote_tweets_count=F('quote_tweets_count') + increment
            )
            return True
        except:
            return False
    
    async def get_trending_posts(self, limit: int = 20) -> List[PostEntity]:
        """Get trending posts based on engagement."""
        # Simple trending algorithm - could be more sophisticated
        dbos = Post.objects.select_related('author').order_by(
            '-likes_count', '-retweets_count', '-created_at'
        )[:limit]
        return [self.mapper.dbo_to_entity(dbo) async for dbo in dbos]


class FollowRepositoryAdapter(FollowRepositoryPort):
    """Repository adapter for Follow operations."""
    
    def __init__(self):
        self.mapper = FollowDBMapper()
    
    async def save(self, follow: FollowEntity) -> FollowEntity:
        """Save a follow relationship."""
        follow_data = self.mapper.entity_to_dbo_data(follow)
        dbo = await Follow.objects.acreate(**follow_data)
        return self.mapper.dbo_to_entity(dbo)
    
    async def find_follow(self, follower_id: int, followed_id: int) -> Optional[FollowEntity]:
        """Find a follow relationship."""
        try:
            dbo = await Follow.objects.aget(follower_id=follower_id, followed_id=followed_id)
            return self.mapper.dbo_to_entity(dbo)
        except Follow.DoesNotExist:
            return None
    
    async def delete_follow(self, follower_id: int, followed_id: int) -> bool:
        """Delete a follow relationship."""
        try:
            await Follow.objects.filter(follower_id=follower_id, followed_id=followed_id).adelete()
            return True
        except:
            return False
    
    async def get_followers(self, user_id: int, limit: int) -> List[FollowEntity]:
        """Get followers of a user."""
        dbos = Follow.objects.filter(followed_id=user_id, status=Follow.FollowStatus.ACTIVE).order_by('-created_at')[:limit]
        return [self.mapper.dbo_to_entity(dbo) async for dbo in dbos]
    
    async def get_following(self, user_id: int, limit: int) -> List[FollowEntity]:
        """Get users that a user is following."""
        dbos = Follow.objects.filter(follower_id=user_id, status=Follow.FollowStatus.ACTIVE).order_by('-created_at')[:limit]
        return [self.mapper.dbo_to_entity(dbo) async for dbo in dbos]


class LikeRepositoryAdapter(LikeRepositoryPort):
    """Repository adapter for Like operations."""
    
    def __init__(self):
        self.mapper = LikeDBMapper()
    
    async def save(self, like: LikeEntity) -> LikeEntity:
        """Save a like."""
        like_data = self.mapper.entity_to_dbo_data(like)
        dbo = await Like.objects.acreate(**like_data)
        return self.mapper.dbo_to_entity(dbo)
    
    async def find_like(self, user_id: int, post_id: int) -> Optional[LikeEntity]:
        """Find a like relationship."""
        try:
            dbo = await Like.objects.aget(user_id=user_id, post_id=post_id)
            return self.mapper.dbo_to_entity(dbo)
        except Like.DoesNotExist:
            return None
    
    async def delete_like(self, user_id: int, post_id: int) -> bool:
        """Delete a like relationship."""
        try:
            await Like.objects.filter(user_id=user_id, post_id=post_id).adelete()
            return True
        except:
            return False
    
    async def increment_post_likes(self, post_id: int, increment: int = 1) -> bool:
        """Increment/decrement the likes count for a post."""
        try:
            await Post.objects.filter(id=post_id).aupdate(
                likes_count=F('likes_count') + increment
            )
            return True
        except:
            return False
