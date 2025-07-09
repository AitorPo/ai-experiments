"""
Post domain entity for Twitter clone.
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field

from .mixins import ToDictMixin


class PostType(str, Enum):
    """Types of posts in the social media platform."""
    ORIGINAL = "original"
    RETWEET = "retweet"
    QUOTE_TWEET = "quote_tweet"
    REPLY = "reply"


class PostVisibility(str, Enum):
    """Visibility levels for posts."""
    PUBLIC = "public"
    FOLLOWERS_ONLY = "followers_only"
    PRIVATE = "private"


class MediaType(str, Enum):
    """Types of media that can be attached to posts."""
    IMAGE = "image"
    VIDEO = "video"
    GIF = "gif"


class MediaAttachment(BaseModel):
    """Media attachment for a post."""
    id: str
    media_type: MediaType
    url: str
    thumbnail_url: Optional[str] = None
    alt_text: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class PostEntity(BaseModel, ToDictMixin):
    """Post entity representing a social media post (tweet)."""
    
    id: Optional[int] = None
    author_id: int
    content: str = Field(..., max_length=280)
    post_type: PostType = PostType.ORIGINAL
    visibility: PostVisibility = PostVisibility.PUBLIC
    
    # Reply/thread information
    reply_to_post_id: Optional[int] = None
    reply_to_user_id: Optional[int] = None
    thread_id: Optional[int] = None  # For threading replies
    
    # Retweet/quote information
    original_post_id: Optional[int] = None
    quote_comment: Optional[str] = Field(default=None, max_length=280)
    
    # Media attachments
    media_attachments: List[MediaAttachment] = Field(default_factory=list)
    
    # Engagement metrics
    likes_count: int = Field(default=0, ge=0)
    retweets_count: int = Field(default=0, ge=0)
    replies_count: int = Field(default=0, ge=0)
    quote_tweets_count: int = Field(default=0, ge=0)
    
    # Post metadata
    is_pinned: bool = False
    is_sensitive: bool = False  # For sensitive content warning
    language: Optional[str] = Field(default="en", max_length=10)
    
    # Timestamps
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        """Pydantic configuration."""
        from_attributes = True
        arbitrary_types_allowed = True

    def is_reply(self) -> bool:
        """Check if this post is a reply to another post."""
        return self.post_type == PostType.REPLY and self.reply_to_post_id is not None
    
    def is_retweet(self) -> bool:
        """Check if this post is a retweet."""
        return self.post_type in [PostType.RETWEET, PostType.QUOTE_TWEET]
    
    def has_media(self) -> bool:
        """Check if post has media attachments."""
        return len(self.media_attachments) > 0
    
    def get_engagement_total(self) -> int:
        """Get total engagement count."""
        return (
            self.likes_count + 
            self.retweets_count + 
            self.replies_count + 
            self.quote_tweets_count
        )
    
    def can_be_retweeted(self) -> bool:
        """Check if post can be retweeted based on visibility."""
        return self.visibility == PostVisibility.PUBLIC
    
    def get_display_content(self) -> str:
        """Get content for display with length validation."""
        if self.is_sensitive:
            return "[Content warning: Click to view]"
        return self.content[:280]  # Ensure Twitter character limit
    
    def validate_content_length(self) -> bool:
        """Validate that content meets length requirements."""
        content_text = str(self.content) if self.content else ""
        if not content_text or len(content_text.strip()) == 0:
            return False
        return len(content_text) <= 280 