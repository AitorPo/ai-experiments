"""
Like repository port interface for the Twitter clone application.
"""

from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.like import LikeEntity


class LikeRepositoryPort(ABC):
    """Port interface for like repository operations."""
    
    @abstractmethod
    async def save(self, like: LikeEntity) -> LikeEntity:
        """Save a like relationship."""
        pass
    
    @abstractmethod
    async def find_like(self, user_id: int, post_id: int) -> Optional[LikeEntity]:
        """Find a like relationship between a user and post."""
        pass
    
    @abstractmethod
    async def delete_like(self, user_id: int, post_id: int) -> bool:
        """Delete a like relationship."""
        pass
    
    @abstractmethod
    async def increment_post_likes(self, post_id: int, increment: int = 1) -> bool:
        """Increment/decrement the likes count for a post."""
        pass 