"""
Follow repository port interface for the Twitter clone application.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.follow import FollowEntity


class FollowRepositoryPort(ABC):
    """Port interface for follow repository operations."""
    
    @abstractmethod
    async def save(self, follow: FollowEntity) -> FollowEntity:
        """Save a follow relationship."""
        pass
    
    @abstractmethod
    async def find_follow(self, follower_id: int, followed_id: int) -> Optional[FollowEntity]:
        """Find a follow relationship between two users."""
        pass
    
    @abstractmethod
    async def delete_follow(self, follower_id: int, followed_id: int) -> bool:
        """Delete a follow relationship."""
        pass
    
    @abstractmethod
    async def get_followers(self, user_id: int, limit: int) -> List[FollowEntity]:
        """Get all followers of a user."""
        pass
    
    @abstractmethod
    async def get_following(self, user_id: int, limit: int) -> List[FollowEntity]:
        """Get all users that a user is following."""
        pass 