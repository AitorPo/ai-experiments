"""
Post repository port interface for data persistence.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.post import PostEntity


class PostRepositoryPort(ABC):
    """Port interface for post repository operations."""
    
    @abstractmethod
    async def save(self, post: PostEntity) -> PostEntity:
        """Save a post to the database."""
        pass
    
    @abstractmethod
    async def find_by_id(self, post_id: int) -> Optional[PostEntity]:
        """Find a post by ID."""
        pass
    
    @abstractmethod
    async def find_by_author(
        self, 
        author_id: int, 
        limit: int, 
        offset: int = 0
    ) -> List[PostEntity]:
        """Find all posts by a specific author."""
        pass
    
    @abstractmethod
    async def find_replies(self, post_id: int, limit: int) -> List[PostEntity]:
        """Find replies to a specific post."""
        pass
    
    @abstractmethod
    async def find_user_retweet(
        self, 
        user_id: int, 
        original_post_id: int
    ) -> Optional[PostEntity]:
        """Find if user has retweeted a specific post."""
        pass
    
    @abstractmethod
    async def get_timeline_posts(
        self, 
        user_id: int, 
        limit: int, 
        offset: int = 0
    ) -> List[PostEntity]:
        """Get timeline posts for a user (posts from followed users)."""
        pass
    
    @abstractmethod
    async def search_posts(self, query: str, limit: int) -> List[PostEntity]:
        """Search posts by content."""
        pass
    
    @abstractmethod
    async def delete_by_id(self, post_id: int) -> bool:
        """Delete a post by ID."""
        pass
    
    @abstractmethod
    async def increment_likes_count(self, post_id: int) -> bool:
        """Increment the likes count for a post."""
        pass
    
    @abstractmethod
    async def increment_retweets_count(self, post_id: int) -> bool:
        """Increment the retweets count for a post."""
        pass
    
    @abstractmethod
    async def increment_replies_count(self, post_id: int) -> bool:
        """Increment the replies count for a post."""
        pass
    
    @abstractmethod
    async def increment_quote_tweets_count(self, post_id: int) -> bool:
        """Increment the quote tweets count for a post."""
        pass
    
    @abstractmethod
    async def get_trending_posts(self, limit: int = 20) -> List[PostEntity]:
        """Get trending posts based on engagement."""
        pass 