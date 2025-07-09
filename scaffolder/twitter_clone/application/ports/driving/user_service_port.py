"""
User service port interface for Twitter clone.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.user import UserEntity


class UserServicePort(ABC):
    """Port interface for user service operations."""
    
    @abstractmethod
    async def register_user(self, user: UserEntity, password: str) -> UserEntity:
        """Register a new user."""
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: int) -> Optional[UserEntity]:
        """Retrieve a user by ID."""
        pass
    
    @abstractmethod
    async def get_user_by_username(self, username: str) -> Optional[UserEntity]:
        """Retrieve a user by username."""
        pass
    
    @abstractmethod
    async def update_profile(self, user_id: int, updates: dict) -> Optional[UserEntity]:
        """Update user profile information."""
        pass
    
    @abstractmethod
    async def search_users(self, query: str, limit: int = 20) -> List[UserEntity]:
        """Search for users."""
        pass
    
    @abstractmethod
    async def get_user_stats(self, user_id: int) -> dict:
        """Get user statistics."""
        pass
    
    @abstractmethod
    async def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp."""
        pass
    
    @abstractmethod
    async def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account."""
        pass 