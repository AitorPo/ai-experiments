"""
API DTOs for Twitter clone external communication.
"""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, EmailStr


# User DTOs
class UserRegistrationDTO(BaseModel):
    """DTO for user registration."""
    username: str = Field(..., min_length=3, max_length=30, pattern=r'^[a-zA-Z0-9_]+$')
    email: EmailStr
    password: str = Field(..., min_length=8)
    display_name: str = Field(..., min_length=1, max_length=50)
    bio: Optional[str] = Field(default="", max_length=160)


class UserLoginDTO(BaseModel):
    """DTO for user login."""
    username: str
    password: str


class UserProfileUpdateDTO(BaseModel):
    """DTO for updating user profile."""
    display_name: Optional[str] = Field(None, min_length=1, max_length=50)
    bio: Optional[str] = Field(None, max_length=160)
    location: Optional[str] = Field(None, max_length=50)
    website: Optional[str] = None
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None


class UserResponseDTO(BaseModel):
    """DTO for user information in responses."""
    id: int
    username: str
    display_name: str
    bio: str
    avatar_url: Optional[str] = None
    banner_url: Optional[str] = None
    location: Optional[str] = None
    website: Optional[str] = None
    followers_count: int
    following_count: int
    posts_count: int
    is_verified: bool
    is_private: bool
    date_joined: datetime
    
    class Config:
        from_attributes = True


class UserProfileDTO(UserResponseDTO):
    """Extended user profile DTO with additional info."""
    is_following: Optional[bool] = None  # Set based on current user context
    is_followed_by: Optional[bool] = None


# Post DTOs
class MediaAttachmentDTO(BaseModel):
    """DTO for media attachments."""
    media_type: str  # image, video, gif
    url: str
    thumbnail_url: Optional[str] = None
    alt_text: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None


class PostCreateDTO(BaseModel):
    """DTO for creating a new post."""
    content: str = Field(..., min_length=1, max_length=280)
    visibility: str = Field(default="public")  # public, followers_only, private
    media_attachments: List[MediaAttachmentDTO] = Field(default_factory=list)
    is_sensitive: bool = False


class ReplyCreateDTO(BaseModel):
    """DTO for creating a reply."""
    content: str = Field(..., min_length=1, max_length=280)
    reply_to_post_id: int
    media_attachments: List[MediaAttachmentDTO] = Field(default_factory=list)


class QuoteTweetCreateDTO(BaseModel):
    """DTO for creating a quote tweet."""
    original_post_id: int
    quote_comment: str = Field(..., min_length=1, max_length=280)
    media_attachments: List[MediaAttachmentDTO] = Field(default_factory=list)


class PostResponseDTO(BaseModel):
    """DTO for post information in responses."""
    id: int
    author: UserResponseDTO
    content: str
    post_type: str  # original, retweet, quote_tweet, reply
    visibility: str
    
    # Reply/thread information
    reply_to_post_id: Optional[int] = None
    reply_to_user: Optional[UserResponseDTO] = None
    thread_id: Optional[int] = None
    
    # Retweet/quote information
    original_post_id: Optional[int] = None
    original_post: Optional['PostResponseDTO'] = None
    quote_comment: Optional[str] = None
    
    # Media attachments
    media_attachments: List[MediaAttachmentDTO] = Field(default_factory=list)
    
    # Engagement metrics
    likes_count: int
    retweets_count: int
    replies_count: int
    quote_tweets_count: int
    
    # User interaction status (set based on current user context)
    is_liked: Optional[bool] = None
    is_retweeted: Optional[bool] = None
    
    # Post metadata
    is_pinned: bool
    is_sensitive: bool
    language: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class TimelineResponseDTO(BaseModel):
    """DTO for timeline responses."""
    posts: List[PostResponseDTO]
    next_cursor: Optional[str] = None
    has_more: bool = False


class PostStatsDTO(BaseModel):
    """DTO for post statistics."""
    likes_count: int
    retweets_count: int
    replies_count: int
    quote_tweets_count: int


# Social interaction DTOs
class FollowActionDTO(BaseModel):
    """DTO for follow actions."""
    user_id: int


class FollowResponseDTO(BaseModel):
    """DTO for follow relationship response."""
    id: int
    follower: UserResponseDTO
    followed: UserResponseDTO
    status: str  # active, pending, blocked, muted
    notifications_enabled: bool
    show_retweets: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class FollowersListDTO(BaseModel):
    """DTO for followers/following list."""
    users: List[UserResponseDTO]
    next_cursor: Optional[str] = None
    has_more: bool = False


class LikeResponseDTO(BaseModel):
    """DTO for like response."""
    id: int
    user: UserResponseDTO
    post_id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


# Search DTOs
class SearchUsersDTO(BaseModel):
    """DTO for user search."""
    query: str = Field(..., min_length=2)
    limit: int = Field(default=20, le=100)


class SearchPostsDTO(BaseModel):
    """DTO for post search."""
    query: str = Field(..., min_length=2)
    limit: int = Field(default=20, le=100)


class SearchResponseDTO(BaseModel):
    """DTO for search responses."""
    users: List[UserResponseDTO] = Field(default_factory=list)
    posts: List[PostResponseDTO] = Field(default_factory=list)
    next_cursor: Optional[str] = None
    has_more: bool = False


# Trending DTOs
class HashtagDTO(BaseModel):
    """DTO for hashtag information."""
    name: str
    usage_count: int
    trending_score: float


class TrendingResponseDTO(BaseModel):
    """DTO for trending topics."""
    hashtags: List[HashtagDTO]
    posts: List[PostResponseDTO] = Field(default_factory=list)


# Error DTOs
class ErrorResponseDTO(BaseModel):
    """DTO for error responses."""
    error: str
    message: str
    details: Optional[dict] = None


class ValidationErrorDTO(BaseModel):
    """DTO for validation error responses."""
    error: str = "validation_error"
    message: str
    field_errors: dict


# Pagination DTOs
class PaginatedResponseDTO(BaseModel):
    """Base DTO for paginated responses."""
    count: int
    next: Optional[str] = None
    previous: Optional[str] = None
    results: List[BaseModel]


# Update PostResponseDTO to handle self-reference
PostResponseDTO.model_rebuild()
