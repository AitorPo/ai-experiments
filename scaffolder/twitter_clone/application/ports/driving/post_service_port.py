"""
Post service port interface for Twitter clone.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from domain.entities.post import PostEntity


class PostServicePort(ABC):
    """Port interface for post service operations."""
    
    @abstractmethod
    async def create_post(self, post: PostEntity) -> PostEntity:
        """Create a new post."""
        pass
    
    @abstractmethod
    async def create_reply(
        self, 
        content: str, 
        author_id: int, 
        reply_to_post_id: int
    ) -> PostEntity:
        """Create a reply to an existing post."""
        pass
    
    @abstractmethod
    async def create_retweet(self, user_id: int, original_post_id: int) -> PostEntity:
        """Create a retweet of an existing post."""
        pass
    
    @abstractmethod
    async def create_quote_tweet(
        self, 
        user_id: int, 
        original_post_id: int, 
        quote_comment: str
    ) -> PostEntity:
        """Create a quote tweet with additional commentary."""
        pass
    
    @abstractmethod
    async def get_post(self, post_id: int) -> Optional[PostEntity]:
        """Retrieve a post by ID."""
        pass
    
    @abstractmethod
    async def get_user_timeline(
        self, 
        user_id: int, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[PostEntity]:
        """Get posts from users that the given user follows."""
        pass
    
    @abstractmethod
    async def get_user_posts(
        self, 
        user_id: int, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[PostEntity]:
        """Get all posts by a specific user."""
        pass
    
    @abstractmethod
    async def get_post_replies(self, post_id: int, limit: int = 20) -> List[PostEntity]:
        """Get replies to a specific post."""
        pass
    
    @abstractmethod
    async def delete_post(self, post_id: int, user_id: int) -> bool:
        """Delete a post."""
        pass
    
    @abstractmethod
    async def search_posts(self, query: str, limit: int = 20) -> List[PostEntity]:
        """Search posts by content."""
        pass 