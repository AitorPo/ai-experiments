"""
REST API adapter implementing Twitter clone API endpoints.
"""

from typing import List, Optional
from django.http import JsonResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from asgiref.sync import sync_to_async, async_to_sync
import json
import asyncio

from application.services.user_service import UserService
from application.services.post_service import PostService
from application.services.social_service import SocialService
from .models import (
    UserRegistrationDTO, UserLoginDTO, UserProfileUpdateDTO,
    PostCreateDTO, ReplyCreateDTO, QuoteTweetCreateDTO,
    FollowActionDTO, SearchUsersDTO, SearchPostsDTO,
    ErrorResponseDTO, ValidationErrorDTO
)
from .mapper import EntityDTOMapper


class TwitterAPIAdapter:
    """REST API adapter for Twitter clone."""
    
    def __init__(
        self,
        user_service: UserService,
        post_service: PostService,
        social_service: SocialService
    ):
        """Initialize adapter with service dependencies."""
        self.user_service = user_service
        self.post_service = post_service
        self.social_service = social_service
        self.mapper = EntityDTOMapper()
    
    # Authentication endpoints
    async def register_user(self, request):
        """Register a new user account."""
        try:
            data = json.loads(request.body)
            registration_dto = UserRegistrationDTO(**data)
            
            # Convert DTO to entity
            user_entity = self.mapper.registration_dto_to_entity(registration_dto)
            
            # Register user
            created_user = await self.user_service.register_user(
                user_entity, 
                registration_dto.password
            )
            
            # Convert to response DTO
            response_dto = self.mapper.user_entity_to_response_dto(created_user)
            
            return JsonResponse({
                "message": "User registered successfully",
                "user": response_dto.model_dump()
            }, status=201)
            
        except ValueError as e:
            error_dto = ValidationErrorDTO(
                message=str(e),
                field_errors={}
            )
            return JsonResponse(error_dto.model_dump(), status=400)
        except Exception as e:
            error_dto = ErrorResponseDTO(
                error="registration_failed",
                message=str(e)
            )
            return JsonResponse(error_dto.model_dump(), status=500)
    
    def login_user(self, request):
        """Authenticate and login a user."""
        try:
            data = json.loads(request.body)
            login_dto = UserLoginDTO(**data)
            
            # Authenticate user
            user = authenticate(
                request,
                username=login_dto.username,
                password=login_dto.password
            )
            
            if user is not None:
                login(request, user)
                
                # Update last login
                asyncio.create_task(
                    self.user_service.update_last_login(user.id)
                )
                
                # Convert to response DTO
                user_entity = self.mapper.django_user_to_entity(user)
                response_dto = self.mapper.user_entity_to_response_dto(user_entity)
                
                return JsonResponse({
                    "message": "Login successful",
                    "user": response_dto.model_dump()
                })
            else:
                error_dto = ErrorResponseDTO(
                    error="authentication_failed",
                    message="Invalid username or password"
                )
                return JsonResponse(error_dto.model_dump(), status=401)
                
        except Exception as e:
            error_dto = ErrorResponseDTO(
                error="login_failed",
                message=str(e)
            )
            return JsonResponse(error_dto.model_dump(), status=500)
    
    def logout_user(self, request):
        """Logout the current user."""
        logout(request)
        return JsonResponse({"message": "Logout successful"})
    
    # User management endpoints
    async def get_user_profile(self, request, username: str):
        """Get a user's profile by username."""
        try:
            user = await self.user_service.get_user_by_username(username)
            if not user:
                error_dto = ErrorResponseDTO(
                    error="user_not_found",
                    message="User not found"
                )
                return JsonResponse(error_dto.model_dump(), status=404)
            
            # Convert to response DTO
            response_dto = self.mapper.user_entity_to_profile_dto(
                user, 
                current_user_id=getattr(request.user, 'id', None)
            )
            
            return JsonResponse(response_dto.model_dump())
            
        except Exception as e:
            error_dto = ErrorResponseDTO(
                error="profile_fetch_failed",
                message=str(e)
            )
            return JsonResponse(error_dto.model_dump(), status=500)
    
    async def update_user_profile(self, request):
        """Update the current user's profile."""
        try:
            data = json.loads(request.body)
            update_dto = UserProfileUpdateDTO(**data)
            
            # Update profile
            updated_user = await self.user_service.update_profile(
                request.user.id,
                update_dto.model_dump(exclude_none=True)
            )
            
            if updated_user:
                response_dto = self.mapper.user_entity_to_response_dto(updated_user)
                return JsonResponse({
                    "message": "Profile updated successfully",
                    "user": response_dto.model_dump()
                })
            else:
                error_dto = ErrorResponseDTO(
                    error="user_not_found",
                    message="User not found"
                )
                return JsonResponse(error_dto.model_dump(), status=404)
                
        except ValueError as e:
            error_dto = ValidationErrorDTO(
                message=str(e),
                field_errors={}
            )
            return JsonResponse(error_dto.model_dump(), status=400)
        except Exception as e:
            error_dto = ErrorResponseDTO(
                error="profile_update_failed",
                message=str(e)
            )
            return JsonResponse(error_dto.model_dump(), status=500)
    
    # Post management endpoints
    async def create_post(self, request):
        """Create a new post."""
        try:
            data = json.loads(request.body)
            post_dto = PostCreateDTO(**data)
            
            # Convert DTO to entity
            post_entity = self.mapper.post_create_dto_to_entity(
                post_dto, 
                request.user.id
            )
            
            # Create post
            created_post = await self.post_service.create_post(post_entity)
            
            # Convert to response DTO
            response_dto = await self.mapper.post_entity_to_response_dto(
                created_post,
                current_user_id=request.user.id
            )
            
            return JsonResponse({
                "message": "Post created successfully",
                "post": response_dto.model_dump()
            }, status=201)
            
        except ValueError as e:
            error_dto = ValidationErrorDTO(
                message=str(e),
                field_errors={}
            )
            return JsonResponse(error_dto.model_dump(), status=400)
        except Exception as e:
            error_dto = ErrorResponseDTO(
                error="post_creation_failed",
                message=str(e)
            )
            return JsonResponse(error_dto.model_dump(), status=500)
    
    async def create_reply(self, request):
        """Create a reply to a post."""
        try:
            data = json.loads(request.body)
            reply_dto = ReplyCreateDTO(**data)
            
            # Create reply
            created_reply = await self.post_service.create_reply(
                reply_dto.content,
                request.user.id,
                reply_dto.reply_to_post_id
            )
            
            # Convert to response DTO
            response_dto = await self.mapper.post_entity_to_response_dto(
                created_reply,
                current_user_id=request.user.id
            )
            
            return JsonResponse({
                "message": "Reply created successfully",
                "post": response_dto.model_dump()
            }, status=201)
            
        except ValueError as e:
            error_dto = ValidationErrorDTO(
                message=str(e),
                field_errors={}
            )
            return JsonResponse(error_dto.model_dump(), status=400)
        except Exception as e:
            error_dto = ErrorResponseDTO(
                error="reply_creation_failed",
                message=str(e)
            )
            return JsonResponse(error_dto.model_dump(), status=500)
    
    async def create_retweet(self, request, post_id: int):
        """Create a retweet of an existing post."""
        try:
            created_retweet = await self.post_service.create_retweet(
                request.user.id,
                post_id
            )
            
            response_dto = await self.mapper.post_entity_to_response_dto(
                created_retweet,
                current_user_id=request.user.id
            )
            
            return JsonResponse({
                "message": "Retweeted successfully",
                "post": response_dto.model_dump()
            }, status=201)
            
        except ValueError as e:
            error_dto = ValidationErrorDTO(
                message=str(e),
                field_errors={}
            )
            return JsonResponse(error_dto.model_dump(), status=400)
        except Exception as e:
            error_dto = ErrorResponseDTO(
                error="retweet_failed",
                message=str(e)
            )
            return JsonResponse(error_dto.model_dump(), status=500)
    
    async def create_quote_tweet(self, request):
        """Create a quote tweet."""
        try:
            data = json.loads(request.body)
            quote_dto = QuoteTweetCreateDTO(**data)
            
            created_quote = await self.post_service.create_quote_tweet(
                request.user.id,
                quote_dto.original_post_id,
                quote_dto.quote_comment
            )
            
            response_dto = await self.mapper.post_entity_to_response_dto(
                created_quote,
                current_user_id=request.user.id
            )
            
            return JsonResponse({
                "message": "Quote tweet created successfully",
                "post": response_dto.model_dump()
            }, status=201)
            
        except ValueError as e:
            error_dto = ValidationErrorDTO(
                message=str(e),
                field_errors={}
            )
            return JsonResponse(error_dto.model_dump(), status=400)
        except Exception as e:
            error_dto = ErrorResponseDTO(
                error="quote_tweet_failed",
                message=str(e)
            )
            return JsonResponse(error_dto.model_dump(), status=500)
    
    async def get_post(self, request, post_id: int):
        """Get a specific post by ID."""
        try:
            post = await self.post_service.get_post(post_id)
            if not post:
                error_dto = ErrorResponseDTO(
                    error="post_not_found",
                    message="Post not found"
                )
                return JsonResponse(error_dto.model_dump(), status=404)
            
            response_dto = await self.mapper.post_entity_to_response_dto(
                post,
                current_user_id=getattr(request.user, 'id', None)
            )
            
            return JsonResponse(response_dto.model_dump())
            
        except Exception as e:
            error_dto = ErrorResponseDTO(
                error="post_fetch_failed",
                message=str(e)
            )
            return JsonResponse(error_dto.model_dump(), status=500)
    
    async def get_timeline(self, request):
        """Get the user's timeline."""
        try:
            limit = int(request.GET.get('limit', 20))
            offset = int(request.GET.get('offset', 0))
            
            posts = await self.post_service.get_user_timeline(
                request.user.id,
                limit,
                offset
            )
            
            # Convert to response DTOs
            response_dtos = []
            for post in posts:
                post_dto = await self.mapper.post_entity_to_response_dto(
                    post,
                    current_user_id=request.user.id
                )
                response_dtos.append(post_dto.model_dump())
            
            return JsonResponse({
                "posts": response_dtos,
                "has_more": len(posts) == limit
            })
            
        except Exception as e:
            error_dto = ErrorResponseDTO(
                error="timeline_fetch_failed",
                message=str(e)
            )
            return JsonResponse(error_dto.model_dump(), status=500)
    
    async def get_user_posts(self, request, username: str):
        """Get posts by a specific user."""
        try:
            user = await self.user_service.get_user_by_username(username)
            if not user:
                error_dto = ErrorResponseDTO(
                    error="user_not_found",
                    message="User not found"
                )
                return JsonResponse(error_dto.model_dump(), status=404)
            
            limit = int(request.GET.get('limit', 20))
            offset = int(request.GET.get('offset', 0))
            
            posts = await self.post_service.get_user_posts(
                user.id,
                limit,
                offset
            )
            
            # Convert to response DTOs
            response_dtos = []
            for post in posts:
                post_dto = await self.mapper.post_entity_to_response_dto(
                    post,
                    current_user_id=getattr(request.user, 'id', None)
                )
                response_dtos.append(post_dto.model_dump())
            
            return JsonResponse({
                "posts": response_dtos,
                "has_more": len(posts) == limit
            })
            
        except Exception as e:
            error_dto = ErrorResponseDTO(
                error="user_posts_fetch_failed",
                message=str(e)
            )
            return JsonResponse(error_dto.model_dump(), status=500)
    
    # Social interaction endpoints
    async def follow_user(self, request):
        """Follow a user."""
        try:
            data = json.loads(request.body)
            follow_dto = FollowActionDTO(**data)
            
            follow_entity = await self.social_service.follow_user(
                request.user.id,
                follow_dto.user_id
            )
            
            response_dto = self.mapper.follow_entity_to_response_dto(follow_entity)
            
            return JsonResponse({
                "message": "User followed successfully",
                "follow": response_dto.model_dump()
            }, status=201)
            
        except ValueError as e:
            error_dto = ValidationErrorDTO(
                message=str(e),
                field_errors={}
            )
            return JsonResponse(error_dto.model_dump(), status=400)
        except Exception as e:
            error_dto = ErrorResponseDTO(
                error="follow_failed",
                message=str(e)
            )
            return JsonResponse(error_dto.model_dump(), status=500)
    
    async def unfollow_user(self, request, user_id: int):
        """Unfollow a user."""
        try:
            success = await self.social_service.unfollow_user(
                request.user.id,
                user_id
            )
            
            if success:
                return JsonResponse({"message": "User unfollowed successfully"})
            else:
                error_dto = ErrorResponseDTO(
                    error="not_following",
                    message="You are not following this user"
                )
                return JsonResponse(error_dto.model_dump(), status=400)
                
        except Exception as e:
            error_dto = ErrorResponseDTO(
                error="unfollow_failed",
                message=str(e)
            )
            return JsonResponse(error_dto.model_dump(), status=500)
    
    async def like_post(self, request, post_id: int):
        """Like a post."""
        try:
            like_entity = await self.social_service.like_post(
                request.user.id,
                post_id
            )
            
            response_dto = self.mapper.like_entity_to_response_dto(like_entity)
            
            return JsonResponse({
                "message": "Post liked successfully",
                "like": response_dto.model_dump()
            }, status=201)
            
        except ValueError as e:
            error_dto = ValidationErrorDTO(
                message=str(e),
                field_errors={}
            )
            return JsonResponse(error_dto.model_dump(), status=400)
        except Exception as e:
            error_dto = ErrorResponseDTO(
                error="like_failed",
                message=str(e)
            )
            return JsonResponse(error_dto.model_dump(), status=500)
    
    async def unlike_post(self, request, post_id: int):
        """Unlike a post."""
        try:
            success = await self.social_service.unlike_post(
                request.user.id,
                post_id
            )
            
            if success:
                return JsonResponse({"message": "Post unliked successfully"})
            else:
                error_dto = ErrorResponseDTO(
                    error="not_liked",
                    message="You have not liked this post"
                )
                return JsonResponse(error_dto.model_dump(), status=400)
                
        except Exception as e:
            error_dto = ErrorResponseDTO(
                error="unlike_failed",
                message=str(e)
            )
            return JsonResponse(error_dto.model_dump(), status=500)
    
    # Search endpoints
    async def search_users(self, request):
        """Search for users."""
        try:
            query = request.GET.get('q', '')
            limit = int(request.GET.get('limit', 20))
            
            if len(query) < 2:
                error_dto = ValidationErrorDTO(
                    message="Search query must be at least 2 characters",
                    field_errors={'q': 'Too short'}
                )
                return JsonResponse(error_dto.model_dump(), status=400)
            
            users = await self.user_service.search_users(query, limit)
            
            # Convert to response DTOs
            response_dtos = [
                self.mapper.user_entity_to_response_dto(user).model_dump()
                for user in users
            ]
            
            return JsonResponse({
                "users": response_dtos,
                "has_more": len(users) == limit
            })
            
        except Exception as e:
            error_dto = ErrorResponseDTO(
                error="user_search_failed",
                message=str(e)
            )
            return JsonResponse(error_dto.model_dump(), status=500)
    
    async def search_posts(self, request):
        """Search for posts."""
        try:
            query = request.GET.get('q', '')
            limit = int(request.GET.get('limit', 20))
            
            if len(query) < 2:
                error_dto = ValidationErrorDTO(
                    message="Search query must be at least 2 characters",
                    field_errors={'q': 'Too short'}
                )
                return JsonResponse(error_dto.model_dump(), status=400)
            
            posts = await self.post_service.search_posts(query, limit)
            
            # Convert to response DTOs
            response_dtos = []
            for post in posts:
                post_dto = await self.mapper.post_entity_to_response_dto(
                    post,
                    current_user_id=getattr(request.user, 'id', None)
                )
                response_dtos.append(post_dto.model_dump())
            
            return JsonResponse({
                "posts": response_dtos,
                "has_more": len(posts) == limit
            })
            
        except Exception as e:
            error_dto = ErrorResponseDTO(
                error="post_search_failed",
                message=str(e)
            )
            return JsonResponse(error_dto.model_dump(), status=500)


# Create a default adapter instance for URL routing
# In a real application, you would use dependency injection
def get_adapter():
    """Get configured adapter instance with services."""
    # This is a placeholder - in real implementation you'd inject actual services
    from application.services.user_service import UserService
    from application.services.post_service import PostService
    from application.services.social_service import SocialService
    from driven.db.adapter import UserRepositoryAdapter, PostRepositoryAdapter, FollowRepositoryAdapter, LikeRepositoryAdapter
    
    # Create repository adapters
    user_repo = UserRepositoryAdapter()
    post_repo = PostRepositoryAdapter()
    follow_repo = FollowRepositoryAdapter()
    like_repo = LikeRepositoryAdapter()
    
    # Create services
    user_service = UserService(user_repo)
    post_service = PostService(post_repo, user_repo)
    social_service = SocialService(follow_repo, like_repo, user_repo)
    
    return TwitterAPIAdapter(user_service, post_service, social_service)


# Create global adapter instance
_adapter = get_adapter()

# Export adapter methods as module-level functions for URL routing
# These functions properly wrap the adapter methods to work with Django decorators

@csrf_exempt
@require_http_methods(["POST"])
def register_user(request):
    """Register a new user account."""
    return async_to_sync(_adapter.register_user)(request)

@csrf_exempt
@require_http_methods(["POST"])
def login_user(request):
    """Authenticate and login a user."""
    return _adapter.login_user(request)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def logout_user(request):
    """Logout the current user."""
    return _adapter.logout_user(request)

@require_http_methods(["GET"])
def get_user(request, user_id):
    """Get a user's profile by ID."""
    return async_to_sync(_adapter.get_user_profile)(request, user_id)

@csrf_exempt
@require_http_methods(["PUT"])
@login_required
def update_user(request):
    """Update the current user's profile."""
    return async_to_sync(_adapter.update_user_profile)(request)

@require_http_methods(["GET"])
def search_users(request):
    """Search for users."""
    return async_to_sync(_adapter.search_users)(request)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def create_post(request):
    """Create a new post."""
    return async_to_sync(_adapter.create_post)(request)

@require_http_methods(["GET"])
def get_post(request, post_id):
    """Get a post by ID."""
    return async_to_sync(_adapter.get_post)(request, post_id)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def reply_to_post(request, post_id):
    """Reply to a post."""
    return async_to_sync(_adapter.create_reply)(request)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def retweet_post(request, post_id):
    """Retweet a post."""
    return async_to_sync(_adapter.create_retweet)(request, post_id)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def quote_tweet_post(request):
    """Create a quote tweet."""
    return async_to_sync(_adapter.create_quote_tweet)(request)

@require_http_methods(["GET"])
@login_required
def get_timeline(request):
    """Get user's timeline."""
    return async_to_sync(_adapter.get_timeline)(request)

@require_http_methods(["GET"])
def get_user_posts(request, user_id):
    """Get posts by a user."""
    return async_to_sync(_adapter.get_user_posts)(request, user_id)

@require_http_methods(["GET"])
def search_posts(request):
    """Search for posts."""
    return async_to_sync(_adapter.search_posts)(request)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def follow_user(request, user_id):
    """Follow a user."""
    return async_to_sync(_adapter.follow_user)(request)

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def unfollow_user(request, user_id):
    """Unfollow a user."""
    return async_to_sync(_adapter.unfollow_user)(request, user_id)

@csrf_exempt
@require_http_methods(["POST"])
@login_required
def like_post(request, post_id):
    """Like a post."""
    return async_to_sync(_adapter.like_post)(request, post_id)

@csrf_exempt
@require_http_methods(["DELETE"])
@login_required
def unlike_post(request, post_id):
    """Unlike a post."""
    return async_to_sync(_adapter.unlike_post)(request, post_id)
