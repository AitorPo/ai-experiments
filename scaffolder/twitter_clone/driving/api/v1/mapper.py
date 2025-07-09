"""
Mappers for converting between domain entities and API DTOs.
"""

from typing import List, Optional
from datetime import datetime

from domain.entities.user import UserEntity
from domain.entities.post import PostEntity, PostType, PostVisibility, MediaAttachment
from domain.entities.follow import FollowEntity, FollowStatus
from domain.entities.like import LikeEntity
from .models import (
    UserRegistrationDTO, UserResponseDTO, UserProfileDTO,
    PostCreateDTO, PostResponseDTO, MediaAttachmentDTO,
    FollowResponseDTO, LikeResponseDTO
)


class EntityDTOMapper:
    """Mapper for converting between entities and DTOs."""
    
    def registration_dto_to_entity(self, dto: UserRegistrationDTO) -> UserEntity:
        """Convert registration DTO to user entity."""
        return UserEntity(
            username=dto.username,
            email=dto.email,
            display_name=dto.display_name,
            bio=dto.bio or "",
            is_active=True,
            created_at=datetime.utcnow()
        )
    
    def user_entity_to_response_dto(self, entity: UserEntity) -> UserResponseDTO:
        """Convert user entity to response DTO."""
        return UserResponseDTO(
            id=entity.id or 0,
            username=entity.username,
            display_name=entity.display_name,
            bio=entity.bio,
            avatar_url=entity.avatar_url,
            banner_url=entity.banner_url,
            location=entity.location,
            website=entity.website,
            followers_count=entity.followers_count,
            following_count=entity.following_count,
            posts_count=entity.posts_count,
            is_verified=entity.is_verified,
            is_private=entity.is_private,
            date_joined=entity.date_joined or datetime.utcnow()
        )
    
    def user_entity_to_profile_dto(
        self, 
        entity: UserEntity, 
        current_user_id: Optional[int] = None
    ) -> UserProfileDTO:
        """Convert user entity to profile DTO with relationship context."""
        base_dto = self.user_entity_to_response_dto(entity)
        
        # In a real implementation, you'd query the social service
        # to determine is_following and is_followed_by
        return UserProfileDTO(
            **base_dto.model_dump(),
            is_following=None,  # Would be set by service layer
            is_followed_by=None  # Would be set by service layer
        )
    
    def django_user_to_entity(self, django_user) -> UserEntity:
        """Convert Django user to user entity."""
        return UserEntity(
            id=django_user.id,
            username=django_user.username,
            email=django_user.email,
            display_name=getattr(django_user, 'display_name', django_user.username),
            bio=getattr(django_user, 'bio', ''),
            avatar_url=getattr(django_user, 'avatar_url', None),
            banner_url=getattr(django_user, 'banner_url', None),
            location=getattr(django_user, 'location', None),
            website=getattr(django_user, 'website', None),
            followers_count=getattr(django_user, 'followers_count', 0),
            following_count=getattr(django_user, 'following_count', 0),
            posts_count=getattr(django_user, 'posts_count', 0),
            is_verified=getattr(django_user, 'is_verified', False),
            is_private=getattr(django_user, 'is_private', False),
            is_active=django_user.is_active,
            date_joined=getattr(django_user, 'date_joined', django_user.date_joined),
            last_login=django_user.last_login,
            created_at=getattr(django_user, 'created_at', django_user.date_joined),
            updated_at=getattr(django_user, 'updated_at', django_user.date_joined)
        )
    
    def post_create_dto_to_entity(
        self, 
        dto: PostCreateDTO, 
        author_id: int
    ) -> PostEntity:
        """Convert post create DTO to post entity."""
        # Convert media attachments
        media_attachments = [
            MediaAttachment(
                id=str(i),
                media_type=media.media_type,
                url=media.url,
                thumbnail_url=media.thumbnail_url,
                alt_text=media.alt_text,
                width=media.width,
                height=media.height
            )
            for i, media in enumerate(dto.media_attachments)
        ]
        
        return PostEntity(
            author_id=author_id,
            content=dto.content,
            post_type=PostType.ORIGINAL,
            visibility=PostVisibility(dto.visibility),
            media_attachments=media_attachments,
            is_sensitive=dto.is_sensitive,
            created_at=datetime.utcnow()
        )
    
    async def post_entity_to_response_dto(
        self, 
        entity: PostEntity,
        current_user_id: Optional[int] = None
    ) -> PostResponseDTO:
        """Convert post entity to response DTO."""
        # Convert media attachments
        media_dtos = [
            MediaAttachmentDTO(
                media_type=media.media_type,
                url=media.url,
                thumbnail_url=media.thumbnail_url,
                alt_text=media.alt_text,
                width=media.width,
                height=media.height
            )
            for media in entity.media_attachments
        ]
        
        # Create a mock author entity for now
        # In real implementation, this would come from the service layer
        mock_author = UserEntity(
            id=entity.author_id,
            username=f"user_{entity.author_id}",
            display_name=f"User {entity.author_id}",
            email=f"user{entity.author_id}@example.com",
            bio="",
            followers_count=0,
            following_count=0,
            posts_count=0,
            is_verified=False,
            is_private=False,
            date_joined=datetime.utcnow()
        )
        
        author_dto = self.user_entity_to_response_dto(mock_author)
        
        return PostResponseDTO(
            id=entity.id or 0,
            author=author_dto,
            content=entity.content,
            post_type=entity.post_type.value,
            visibility=entity.visibility.value,
            reply_to_post_id=entity.reply_to_post_id,
            reply_to_user=None,  # Would be populated by service
            thread_id=entity.thread_id,
            original_post_id=entity.original_post_id,
            original_post=None,  # Would be populated by service
            quote_comment=entity.quote_comment,
            media_attachments=media_dtos,
            likes_count=entity.likes_count,
            retweets_count=entity.retweets_count,
            replies_count=entity.replies_count,
            quote_tweets_count=entity.quote_tweets_count,
            is_liked=None,  # Would be set by service based on current user
            is_retweeted=None,  # Would be set by service based on current user
            is_pinned=entity.is_pinned,
            is_sensitive=entity.is_sensitive,
            language=entity.language,
            created_at=entity.created_at or datetime.utcnow()
        )
    
    def follow_entity_to_response_dto(self, entity: FollowEntity) -> FollowResponseDTO:
        """Convert follow entity to response DTO."""
        # Create mock user entities - in real implementation, these would come from service
        follower = UserEntity(
            id=entity.follower_id,
            username=f"user_{entity.follower_id}",
            display_name=f"User {entity.follower_id}",
            email=f"user{entity.follower_id}@example.com",
            bio="",
            followers_count=0,
            following_count=0,
            posts_count=0,
            is_verified=False,
            is_private=False,
            date_joined=datetime.utcnow()
        )
        
        followed = UserEntity(
            id=entity.followed_id,
            username=f"user_{entity.followed_id}",
            display_name=f"User {entity.followed_id}",
            email=f"user{entity.followed_id}@example.com",
            bio="",
            followers_count=0,
            following_count=0,
            posts_count=0,
            is_verified=False,
            is_private=False,
            date_joined=datetime.utcnow()
        )
        
        return FollowResponseDTO(
            id=entity.id or 0,
            follower=self.user_entity_to_response_dto(follower),
            followed=self.user_entity_to_response_dto(followed),
            status=entity.status.value,
            notifications_enabled=entity.notifications_enabled,
            show_retweets=entity.show_retweets,
            created_at=entity.created_at or datetime.utcnow()
        )
    
    def like_entity_to_response_dto(self, entity: LikeEntity) -> LikeResponseDTO:
        """Convert like entity to response DTO."""
        # Create mock user entity - in real implementation, this would come from service
        user = UserEntity(
            id=entity.user_id,
            username=f"user_{entity.user_id}",
            display_name=f"User {entity.user_id}",
            email=f"user{entity.user_id}@example.com",
            bio="",
            followers_count=0,
            following_count=0,
            posts_count=0,
            is_verified=False,
            is_private=False,
            date_joined=datetime.utcnow()
        )
        
        return LikeResponseDTO(
            id=entity.id or 0,
            user=self.user_entity_to_response_dto(user),
            post_id=entity.post_id,
            created_at=entity.created_at or datetime.utcnow()
        )
    
    def entities_to_response_dtos(self, entities: List[UserEntity]) -> List[UserResponseDTO]:
        """Convert list of user entities to response DTOs."""
        return [self.user_entity_to_response_dto(entity) for entity in entities]
