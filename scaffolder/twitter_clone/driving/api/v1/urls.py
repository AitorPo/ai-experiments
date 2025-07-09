"""
URL configuration for API v1 endpoints.
"""

from django.urls import path
from . import adapter

urlpatterns = [
    # Authentication endpoints
    path("auth/register/", adapter.register_user, name="auth-register"),
    path("auth/login/", adapter.login_user, name="auth-login"),
    path("auth/logout/", adapter.logout_user, name="auth-logout"),
    
    # User endpoints
    path("users/<int:user_id>/", adapter.get_user, name="user-detail"),
    path("users/<int:user_id>/update/", adapter.update_user, name="user-update"),
    path("users/search/", adapter.search_users, name="user-search"),
    
    # Post endpoints
    path("posts/", adapter.create_post, name="post-create"),
    path("posts/<int:post_id>/", adapter.get_post, name="post-detail"),
    path("posts/<int:post_id>/reply/", adapter.reply_to_post, name="post-reply"),
    path("posts/<int:post_id>/retweet/", adapter.retweet_post, name="post-retweet"),
    path("posts/<int:post_id>/quote/", adapter.quote_tweet_post, name="post-quote"),
    path("posts/timeline/", adapter.get_timeline, name="post-timeline"),
    path("users/<int:user_id>/posts/", adapter.get_user_posts, name="user-posts"),
    path("posts/search/", adapter.search_posts, name="post-search"),
    
    # Social endpoints
    path("users/<int:user_id>/follow/", adapter.follow_user, name="social-follow"),
    path("users/<int:user_id>/unfollow/", adapter.unfollow_user, name="social-unfollow"),
    path("posts/<int:post_id>/like/", adapter.like_post, name="social-like"),
    path("posts/<int:post_id>/unlike/", adapter.unlike_post, name="social-unlike"),
]
