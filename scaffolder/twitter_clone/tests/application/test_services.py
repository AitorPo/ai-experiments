"""
Test cases for application services.
"""

import pytest
from unittest.mock import AsyncMock, Mock

from application.services.user_service import UserService
from application.services.post_service import PostService
from application.services.social_service import SocialService
from domain.entities.user import UserEntity
from domain.entities.post import PostEntity, PostType, PostVisibility
from domain.entities.follow import FollowEntity, FollowStatus
from domain.entities.like import LikeEntity


class TestUserService:
    """Test cases for UserService."""
    
    def test_user_service_initialization(self):
        """Test that UserService can be initialized."""
        mock_repo = Mock()
        service = UserService(mock_repo)
        assert service is not None


class TestPostService:
    """Test cases for PostService."""
    
    def test_post_service_initialization(self):
        """Test that PostService can be initialized."""
        mock_repo = Mock()
        mock_user_repo = Mock()
        service = PostService(mock_repo, mock_user_repo)
        assert service is not None


class TestSocialService:
    """Test cases for SocialService."""
    
    def test_social_service_initialization(self):
        """Test that SocialService can be initialized."""
        mock_follow_repo = Mock()
        mock_like_repo = Mock()
        mock_user_repo = Mock()
        mock_post_repo = Mock()
        service = SocialService(mock_follow_repo, mock_like_repo, mock_user_repo, mock_post_repo)
        assert service is not None
