"""
Follow domain entity for Twitter clone.
"""

from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field

from .mixins import ToDictMixin


class FollowStatus(str, Enum):
    """Status of a follow relationship."""
    ACTIVE = "active"
    PENDING = "pending"  # For private accounts
    BLOCKED = "blocked"
    MUTED = "muted"


class FollowEntity(BaseModel, ToDictMixin):
    """Follow entity representing a user following another user."""
    
    id: Optional[int] = None
    follower_id: int  # User who is following
    followed_id: int  # User being followed
    status: FollowStatus = FollowStatus.ACTIVE
    
    # Follow metadata
    notifications_enabled: bool = True  # Get notifications for this user's posts
    show_retweets: bool = True  # Show retweets from this user in timeline
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        arbitrary_types_allowed = True

    def is_active(self) -> bool:
        """Check if the follow relationship is active."""
        return self.status == FollowStatus.ACTIVE
    
    def is_pending(self) -> bool:
        """Check if the follow request is pending approval."""
        return self.status == FollowStatus.PENDING
    
    def is_muted(self) -> bool:
        """Check if the followed user is muted."""
        return self.status == FollowStatus.MUTED
    
    def validate_different_users(self) -> bool:
        """Validate that a user is not trying to follow themselves."""
        return self.follower_id != self.followed_id 