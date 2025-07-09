"""
User service implementing user management business logic.
"""

from typing import List, Optional
from datetime import datetime

from application.ports.driving.user_service_port import UserServicePort
from application.ports.driven.user_repository_port import UserRepositoryPort
from domain.entities.user import UserEntity


class UserService(UserServicePort):
    """Service implementing user management operations."""
    
    def __init__(self, user_repository: UserRepositoryPort):
        """Initialize service with repository dependency."""
        self.user_repository = user_repository
    
    async def register_user(self, user: UserEntity, password: str) -> UserEntity:
        """Register a new user with business validation."""
        # Business validation
        if not user.username or len(user.username.strip()) < 3:
            raise ValueError("Username must be at least 3 characters long")
        
        if not user.email:
            raise ValueError("Email is required")
        
        if not user.display_name or len(user.display_name.strip()) == 0:
            raise ValueError("Display name is required")
        
        if len(password) < 8:
            raise ValueError("Password must be at least 8 characters long")
        
        # Check if username already exists
        existing_user = await self.user_repository.find_by_username(user.username)
        if existing_user:
            raise ValueError("Username already exists")
        
        # Check if email already exists
        existing_email = await self.user_repository.find_by_email(user.email)
        if existing_email:
            raise ValueError("Email already exists")
        
        # Set registration timestamp
        user.date_joined = datetime.utcnow()
        user.created_at = datetime.utcnow()
        
        # Save user with hashed password
        return await self.user_repository.create_user(user, password)
    
    async def get_user_by_id(self, user_id: int) -> Optional[UserEntity]:
        """Retrieve a user by ID."""
        if user_id <= 0:
            raise ValueError("User ID must be positive")
        
        return await self.user_repository.find_by_id(user_id)
    
    async def get_user_by_username(self, username: str) -> Optional[UserEntity]:
        """Retrieve a user by username."""
        if not username or len(username.strip()) == 0:
            raise ValueError("Username cannot be empty")
        
        return await self.user_repository.find_by_username(username.strip())
    
    async def update_profile(self, user_id: int, updates: dict) -> Optional[UserEntity]:
        """Update user profile information."""
        if user_id <= 0:
            raise ValueError("User ID must be positive")
        
        # Get existing user
        existing_user = await self.user_repository.find_by_id(user_id)
        if not existing_user:
            return None
        
        # Validate updates
        if 'bio' in updates and len(updates['bio']) > 160:
            raise ValueError("Bio cannot be longer than 160 characters")
        
        if 'display_name' in updates and len(updates['display_name'].strip()) == 0:
            raise ValueError("Display name cannot be empty")
        
        if 'username' in updates:
            new_username = updates['username'].strip()
            if len(new_username) < 3:
                raise ValueError("Username must be at least 3 characters long")
            
            # Check if new username already exists (excluding current user)
            existing_username = await self.user_repository.find_by_username(new_username)
            if existing_username and existing_username.id != user_id:
                raise ValueError("Username already exists")
        
        # Apply updates
        updates['updated_at'] = datetime.utcnow()
        return await self.user_repository.update_user(user_id, updates)
    
    async def search_users(self, query: str, limit: int = 20) -> List[UserEntity]:
        """Search for users by username or display name."""
        if not query or len(query.strip()) < 2:
            raise ValueError("Search query must be at least 2 characters")
        
        if limit <= 0 or limit > 100:
            limit = 20
        
        return await self.user_repository.search_users(query.strip(), limit)
    
    async def get_user_stats(self, user_id: int) -> dict:
        """Get user statistics (followers, following, posts count)."""
        user = await self.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        return {
            'followers_count': user.followers_count,
            'following_count': user.following_count,
            'posts_count': user.posts_count,
            'is_verified': user.is_verified,
            'date_joined': user.date_joined
        }
    
    async def update_last_login(self, user_id: int) -> bool:
        """Update user's last login timestamp."""
        updates = {'last_login': datetime.utcnow()}
        result = await self.user_repository.update_user(user_id, updates)
        return result is not None
    
    async def deactivate_user(self, user_id: int) -> bool:
        """Deactivate a user account."""
        updates = {
            'is_active': False,
            'updated_at': datetime.utcnow()
        }
        result = await self.user_repository.update_user(user_id, updates)
        return result is not None 