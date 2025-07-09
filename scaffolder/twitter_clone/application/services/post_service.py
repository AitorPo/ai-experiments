"""
Post service implementing post management business logic.
"""

from typing import List, Optional
from datetime import datetime

from application.ports.driving.post_service_port import PostServicePort
from application.ports.driven.post_repository_port import PostRepositoryPort
from application.ports.driven.user_repository_port import UserRepositoryPort
from domain.entities.post import PostEntity, PostType, PostVisibility
from domain.entities.user import UserEntity


class PostService(PostServicePort):
    """Service implementing post management operations."""
    
    def __init__(
        self, 
        post_repository: PostRepositoryPort, 
        user_repository: UserRepositoryPort
    ):
        """Initialize service with repository dependencies."""
        self.post_repository = post_repository
        self.user_repository = user_repository
    
    async def create_post(self, post: PostEntity) -> PostEntity:
        """Create a new post with business validation."""
        # Validate content length
        if not post.validate_content_length():
            raise ValueError("Post content must be between 1 and 280 characters")
        
        # Check if user exists and can post
        user = await self.user_repository.find_by_id(post.author_id)
        if not user:
            raise ValueError("User not found")
        
        if not user.can_post():
            raise ValueError("User is not allowed to post")
        
        # Set creation timestamp
        post.created_at = datetime.utcnow()
        
        # Save post
        created_post = await self.post_repository.save(post)
        
        # Update user's post count
        await self.user_repository.increment_posts_count(user.id)
        
        return created_post
    
    async def create_reply(
        self, 
        content: str, 
        author_id: int, 
        reply_to_post_id: int
    ) -> PostEntity:
        """Create a reply to an existing post."""
        # Check if original post exists
        original_post = await self.post_repository.find_by_id(reply_to_post_id)
        if not original_post:
            raise ValueError("Original post not found")
        
        # Create reply post
        reply = PostEntity(
            author_id=author_id,
            content=content,
            post_type=PostType.REPLY,
            reply_to_post_id=reply_to_post_id,
            reply_to_user_id=original_post.author_id,
            thread_id=original_post.thread_id or original_post.id
        )
        
        created_reply = await self.create_post(reply)
        
        # Update original post's reply count
        await self.post_repository.increment_replies_count(reply_to_post_id)
        
        return created_reply
    
    async def create_retweet(self, user_id: int, original_post_id: int) -> PostEntity:
        """Create a retweet of an existing post."""
        # Check if original post exists and can be retweeted
        original_post = await self.post_repository.find_by_id(original_post_id)
        if not original_post:
            raise ValueError("Original post not found")
        
        if not original_post.can_be_retweeted():
            raise ValueError("Post cannot be retweeted")
        
        # Check if user already retweeted this post
        existing_retweet = await self.post_repository.find_user_retweet(
            user_id, original_post_id
        )
        if existing_retweet:
            raise ValueError("User has already retweeted this post")
        
        # Create retweet
        retweet = PostEntity(
            author_id=user_id,
            content="",  # Retweets don't have content
            post_type=PostType.RETWEET,
            original_post_id=original_post_id
        )
        
        created_retweet = await self.create_post(retweet)
        
        # Update original post's retweet count
        await self.post_repository.increment_retweets_count(original_post_id)
        
        return created_retweet
    
    async def create_quote_tweet(
        self, 
        user_id: int, 
        original_post_id: int, 
        quote_comment: str
    ) -> PostEntity:
        """Create a quote tweet with additional commentary."""
        # Validate quote comment
        if not quote_comment or len(quote_comment.strip()) == 0:
            raise ValueError("Quote comment cannot be empty")
        
        if len(quote_comment) > 280:
            raise ValueError("Quote comment cannot exceed 280 characters")
        
        # Check if original post exists
        original_post = await self.post_repository.find_by_id(original_post_id)
        if not original_post:
            raise ValueError("Original post not found")
        
        # Create quote tweet
        quote_tweet = PostEntity(
            author_id=user_id,
            content=quote_comment,
            post_type=PostType.QUOTE_TWEET,
            original_post_id=original_post_id
        )
        
        created_quote = await self.create_post(quote_tweet)
        
        # Update original post's quote tweet count
        await self.post_repository.increment_quote_tweets_count(original_post_id)
        
        return created_quote
    
    async def get_post(self, post_id: int) -> Optional[PostEntity]:
        """Retrieve a post by ID."""
        if post_id <= 0:
            raise ValueError("Post ID must be positive")
        
        return await self.post_repository.find_by_id(post_id)
    
    async def get_user_timeline(
        self, 
        user_id: int, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[PostEntity]:
        """Get posts from users that the given user follows."""
        if user_id <= 0:
            raise ValueError("User ID must be positive")
        
        if limit <= 0 or limit > 100:
            limit = 20
        
        return await self.post_repository.get_timeline_posts(user_id, limit, offset)
    
    async def get_user_posts(
        self, 
        user_id: int, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[PostEntity]:
        """Get all posts by a specific user."""
        if user_id <= 0:
            raise ValueError("User ID must be positive")
        
        if limit <= 0 or limit > 100:
            limit = 20
        
        return await self.post_repository.find_by_author(user_id, limit, offset)
    
    async def get_post_replies(
        self, 
        post_id: int, 
        limit: int = 20
    ) -> List[PostEntity]:
        """Get replies to a specific post."""
        return await self.post_repository.find_replies(post_id, limit)
    
    async def delete_post(self, post_id: int, user_id: int) -> bool:
        """Delete a post (only by the author)."""
        post = await self.post_repository.find_by_id(post_id)
        if not post:
            return False
        
        # Only the author can delete their own posts
        if post.author_id != user_id:
            raise ValueError("Only the author can delete their own posts")
        
        success = await self.post_repository.delete_by_id(post_id)
        
        if success:
            # Decrement user's post count
            await self.user_repository.increment_posts_count(user_id, -1)
        
        return success
    
    async def search_posts(self, query: str, limit: int = 20) -> List[PostEntity]:
        """Search posts by content."""
        if not query or len(query.strip()) < 2:
            raise ValueError("Search query must be at least 2 characters")
        
        if limit <= 0 or limit > 100:
            limit = 20
        
        return await self.post_repository.search_posts(query.strip(), limit) 