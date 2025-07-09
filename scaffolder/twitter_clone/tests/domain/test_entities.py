"""
Test cases for domain entities.
"""

import pytest
from datetime import datetime

from domain.entities.user import UserEntity
from domain.entities.post import PostEntity, PostType, PostVisibility
from domain.entities.follow import FollowEntity, FollowStatus
from domain.entities.like import LikeEntity


class TestUserEntity:
    """Test cases for UserEntity."""
    
    def test_user_entity_creation(self):
        """Test that a user entity can be created with valid data."""
        entity = UserEntity(
            username="testuser",
            email="test@example.com",
            display_name="Test User",
            bio="Test bio",
            is_active=True
        )
        
        assert entity.username == "testuser"
        assert entity.email == "test@example.com"
        assert entity.display_name == "Test User"
        assert entity.bio == "Test bio"
        assert entity.is_active is True
        assert entity.followers_count == 0
        assert entity.following_count == 0
        assert entity.posts_count == 0
        assert entity.is_verified is False
        assert entity.is_private is False


class TestPostEntity:
    """Test cases for PostEntity."""
    
    def test_post_entity_creation(self):
        """Test that a post entity can be created with valid data."""
        entity = PostEntity(
            author_id=1,
            content="This is a test post",
            post_type=PostType.ORIGINAL,
            visibility=PostVisibility.PUBLIC
        )
        
        assert entity.author_id == 1
        assert entity.content == "This is a test post"
        assert entity.post_type == PostType.ORIGINAL
        assert entity.visibility == PostVisibility.PUBLIC
        assert entity.likes_count == 0
        assert entity.retweets_count == 0
        assert entity.replies_count == 0
        assert entity.quote_tweets_count == 0
        assert entity.is_pinned is False
        assert entity.is_sensitive is False


class TestFollowEntity:
    """Test cases for FollowEntity."""
    
    def test_follow_entity_creation(self):
        """Test that a follow entity can be created with valid data."""
        entity = FollowEntity(
            follower_id=1,
            followed_id=2,
            status=FollowStatus.ACTIVE,
            notifications_enabled=True,
            show_retweets=True
        )
        
        assert entity.follower_id == 1
        assert entity.followed_id == 2
        assert entity.status == FollowStatus.ACTIVE
        assert entity.notifications_enabled is True
        assert entity.show_retweets is True


class TestLikeEntity:
    """Test cases for LikeEntity."""
    
    def test_like_entity_creation(self):
        """Test that a like entity can be created with valid data."""
        entity = LikeEntity(
            user_id=1,
            post_id=2
        )
        
        assert entity.user_id == 1
        assert entity.post_id == 2
