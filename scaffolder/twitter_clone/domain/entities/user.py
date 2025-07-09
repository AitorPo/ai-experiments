"""
User domain entity for Twitter clone.
"""

from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr

from .mixins import ToDictMixin


class UserEntity(BaseModel, ToDictMixin):
    """User entity representing a social media user."""
    
    id: Optional[int] = None
    username: str = Field(..., min_length=3, max_length=30, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    display_name: str = Field(..., min_length=1, max_length=50)
    bio: str = Field(default="", max_length=160)
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    location: Optional[str] = Field(default=None, max_length=50)
    website: Optional[str] = None
    
    # Social stats
    followers_count: int = Field(default=0, ge=0)
    following_count: int = Field(default=0, ge=0)
    posts_count: int = Field(default=0, ge=0)
    
    # Account settings
    is_verified: bool = False
    is_private: bool = False
    is_active: bool = True
    
    # Timestamps
    date_joined: Optional[datetime] = None
    last_login: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        arbitrary_types_allowed = True

    def can_post(self) -> bool:
        """Check if user can create posts."""
        return self.is_active and not self.is_banned()
    
    def is_banned(self) -> bool:
        """Check if user is banned."""
        # Business logic for banning could be implemented here
        return False
    
    def get_full_display_name(self) -> str:
        """Get the full display name with verification status."""
        name = self.display_name
        if self.is_verified:
            name += " ✓"
        return name 