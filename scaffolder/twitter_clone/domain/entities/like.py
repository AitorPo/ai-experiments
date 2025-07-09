"""
Like domain entity for Twitter clone.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from .mixins import ToDictMixin


class LikeEntity(BaseModel, ToDictMixin):
    """Like entity representing a user liking a post."""
    
    id: Optional[int] = None
    user_id: int  # User who liked the post
    post_id: int  # Post that was liked
    
    # Timestamps
    created_at: Optional[datetime] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        arbitrary_types_allowed = True

    def validate_unique_like(self, existing_likes: list) -> bool:
        """Validate that this is not a duplicate like."""
        return not any(
            like.user_id == self.user_id and like.post_id == self.post_id
            for like in existing_likes
        ) 