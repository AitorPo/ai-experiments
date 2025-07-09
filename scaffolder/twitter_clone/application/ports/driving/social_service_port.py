"""
Social service port interface for the Twitter clone application.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.follow import FollowEntity
from domain.entities.like import LikeEntity


class SocialServicePort(ABC):
    """Port interface for social interactions service."""
    
    @abstractmethod
    async def follow_user(self, follower_id: int, followed_id: int) -> FollowEntity:
        """Follow a user."""
        pass
    
    @abstractmethod
    async def unfollow_user(self, follower_id: int, followed_id: int) -> bool:
        """Unfollow a user."""
        pass
    
    @abstractmethod
    async def is_following(self, follower_id: int, followed_id: int) -> bool:
        """Check if a user is following another user."""
        pass
    
    @abstractmethod
    async def get_followers(self, user_id: int, limit: int = 50) -> List[FollowEntity]:
        """Get followers of a user."""
        pass
    
    @abstractmethod
    async def get_following(self, user_id: int, limit: int = 50) -> List[FollowEntity]:
        """Get users that a user is following."""
        pass
    
    @abstractmethod
    async def like_post(self, user_id: int, post_id: int) -> LikeEntity:
        """Like a post."""
        pass
    
    @abstractmethod
    async def unlike_post(self, user_id: int, post_id: int) -> bool:
        """Unlike a post."""
        pass
    
    @abstractmethod
    async def has_liked_post(self, user_id: int, post_id: int) -> bool:
        """Check if a user has liked a post."""
        pass 