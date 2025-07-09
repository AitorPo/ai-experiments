"""
User repository port interface for data persistence.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.user import UserEntity


class UserRepositoryPort(ABC):
    """Port interface for user repository operations."""
    
    @abstractmethod
    async def create_user(self, user: UserEntity, password: str) -> UserEntity:
        """Create a new user with hashed password."""
        pass
    
    @abstractmethod
    async def find_by_id(self, user_id: int) -> Optional[UserEntity]:
        """Find a user by ID."""
        pass
    
    @abstractmethod
    async def find_by_username(self, username: str) -> Optional[UserEntity]:
        """Find a user by username."""
        pass
    
    @abstractmethod
    async def find_by_email(self, email: str) -> Optional[UserEntity]:
        """Find a user by email."""
        pass
    
    @abstractmethod
    async def update_user(self, user_id: int, updates: dict) -> Optional[UserEntity]:
        """Update an existing user."""
        pass
    
    @abstractmethod
    async def search_users(self, query: str, limit: int) -> List[UserEntity]:
        """Search users by username or display name."""
        pass
    
    @abstractmethod
    async def get_followers_count(self, user_id: int) -> int:
        """Get the number of followers for a user."""
        pass
    
    @abstractmethod
    async def get_following_count(self, user_id: int) -> int:
        """Get the number of users being followed."""
        pass
    
    @abstractmethod
    async def increment_posts_count(self, user_id: int) -> bool:
        """Increment the posts count for a user."""
        pass
    
    @abstractmethod
    async def verify_password(self, user_id: int, password: str) -> bool:
        """Verify user password."""
        pass 