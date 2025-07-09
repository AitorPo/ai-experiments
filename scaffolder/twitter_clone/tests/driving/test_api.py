"""
Test cases for driving layer API adapters.
"""

import pytest
from unittest.mock import AsyncMock
from driving.api.v1.adapter import TwitterAPIAdapter
from driving.api.v1.models import UserRegistrationDTO, PostCreateDTO
from application.services.user_service import UserService
from application.services.post_service import PostService
from application.services.social_service import SocialService


class TestTwitterAPIAdapter:
    """Test cases for TwitterAPIAdapter."""
    
    def test_api_adapter_initialization(self):
        """Test that TwitterAPIAdapter can be initialized."""
        mock_user_service = AsyncMock(spec=UserService)
        mock_post_service = AsyncMock(spec=PostService)
        mock_social_service = AsyncMock(spec=SocialService)
        
        adapter = TwitterAPIAdapter(mock_user_service, mock_post_service, mock_social_service)
        assert adapter is not None
        assert adapter.user_service is not None
        assert adapter.post_service is not None
        assert adapter.social_service is not None
