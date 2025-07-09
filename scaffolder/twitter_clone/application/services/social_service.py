"""
Social service implementing follow and like business logic.
"""

from typing import List, Optional
from datetime import datetime

from application.ports.driving.social_service_port import SocialServicePort
from application.ports.driven.follow_repository_port import FollowRepositoryPort
from application.ports.driven.like_repository_port import LikeRepositoryPort
from application.ports.driven.user_repository_port import UserRepositoryPort
from domain.entities.follow import FollowEntity, FollowStatus
from domain.entities.like import LikeEntity


class SocialService(SocialServicePort):
    """Service implementing social interactions (follows and likes)."""
    
    def __init__(
        self,
        follow_repository: FollowRepositoryPort,
        like_repository: LikeRepositoryPort,
        user_repository: UserRepositoryPort
    ):
        """Initialize service with repository dependencies."""
        self.follow_repository = follow_repository
        self.like_repository = like_repository
        self.user_repository = user_repository
    
    async def follow_user(self, follower_id: int, followed_id: int) -> FollowEntity:
        """Follow a user."""
        # Validate that user is not trying to follow themselves
        if follower_id == followed_id:
            raise ValueError("Users cannot follow themselves")
        
        # Check if both users exist
        follower = await self.user_repository.find_by_id(follower_id)
        followed = await self.user_repository.find_by_id(followed_id)
        
        if not follower or not followed:
            raise ValueError("One or both users not found")
        
        # Check if already following
        existing_follow = await self.follow_repository.find_follow(
            follower_id, followed_id
        )
        if existing_follow and existing_follow.is_active():
            raise ValueError("Already following this user")
        
        # Create follow relationship
        follow = FollowEntity(
            follower_id=follower_id,
            followed_id=followed_id,
            status=FollowStatus.PENDING if followed.is_private else FollowStatus.ACTIVE,
            created_at=datetime.utcnow()
        )
        
        created_follow = await self.follow_repository.save(follow)
        
        # Update follower counts if approved immediately
        if created_follow.is_active():
            await self.user_repository.increment_following_count(follower_id)
            await self.user_repository.increment_followers_count(followed_id)
        
        return created_follow
    
    async def unfollow_user(self, follower_id: int, followed_id: int) -> bool:
        """Unfollow a user."""
        follow = await self.follow_repository.find_follow(follower_id, followed_id)
        if not follow or not follow.is_active():
            return False
        
        success = await self.follow_repository.delete_follow(follower_id, followed_id)
        
        if success:
            # Update follower counts
            await self.user_repository.increment_following_count(follower_id, -1)
            await self.user_repository.increment_followers_count(followed_id, -1)
        
        return success
    
    async def like_post(self, user_id: int, post_id: int) -> LikeEntity:
        """Like a post."""
        # Check if already liked
        existing_like = await self.like_repository.find_like(user_id, post_id)
        if existing_like:
            raise ValueError("Post already liked")
        
        # Create like
        like = LikeEntity(
            user_id=user_id,
            post_id=post_id,
            created_at=datetime.utcnow()
        )
        
        created_like = await self.like_repository.save(like)
        
        # Increment post like count
        await self.like_repository.increment_post_likes(post_id)
        
        return created_like
    
    async def unlike_post(self, user_id: int, post_id: int) -> bool:
        """Unlike a post."""
        success = await self.like_repository.delete_like(user_id, post_id)
        
        if success:
            # Decrement post like count
            await self.like_repository.increment_post_likes(post_id, -1)
        
        return success
    
    async def get_followers(
        self, 
        user_id: int, 
        limit: int = 20
    ) -> List[FollowEntity]:
        """Get followers of a user."""
        return await self.follow_repository.get_followers(user_id, limit)
    
    async def get_following(
        self, 
        user_id: int, 
        limit: int = 20
    ) -> List[FollowEntity]:
        """Get users that a user is following."""
        return await self.follow_repository.get_following(user_id, limit)
    
    async def is_following(self, follower_id: int, followed_id: int) -> bool:
        """Check if one user is following another."""
        follow = await self.follow_repository.find_follow(follower_id, followed_id)
        return follow is not None and follow.is_active()
    
    async def has_liked_post(self, user_id: int, post_id: int) -> bool:
        """Check if user has liked a post."""
        like = await self.like_repository.find_like(user_id, post_id)
        return like is not None 