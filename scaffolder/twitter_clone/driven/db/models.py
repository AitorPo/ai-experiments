"""
Django models (Database Objects) for the example domain.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MaxLengthValidator
from django.utils import timezone


class User(AbstractUser):
    """Extended user model for Twitter clone."""
    
    # Override username to allow longer usernames
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[],  # Remove default validators
        help_text='Required. 30 characters or fewer. Letters, digits and _ only.',
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    
    # Profile information
    display_name = models.CharField(max_length=50)
    bio = models.TextField(
        max_length=160,
        blank=True,
        default="",
        validators=[MaxLengthValidator(160)]
    )
    avatar_url = models.URLField(blank=True, null=True)
    banner_url = models.URLField(blank=True, null=True)
    location = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    
    # Social stats (denormalized for performance)
    followers_count = models.PositiveIntegerField(default=0)
    following_count = models.PositiveIntegerField(default=0)
    posts_count = models.PositiveIntegerField(default=0)
    
    # Account settings
    is_verified = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['display_name']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"@{self.username}"


class Post(models.Model):
    """Post model representing tweets."""
    
    class PostType(models.TextChoices):
        ORIGINAL = 'original', 'Original'
        RETWEET = 'retweet', 'Retweet'
        QUOTE_TWEET = 'quote_tweet', 'Quote Tweet'
        REPLY = 'reply', 'Reply'
    
    class PostVisibility(models.TextChoices):
        PUBLIC = 'public', 'Public'
        FOLLOWERS_ONLY = 'followers_only', 'Followers Only'
        PRIVATE = 'private', 'Private'
    
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    content = models.TextField(
        max_length=280,
        validators=[MaxLengthValidator(280)]
    )
    post_type = models.CharField(
        max_length=20,
        choices=PostType.choices,
        default=PostType.ORIGINAL
    )
    visibility = models.CharField(
        max_length=20,
        choices=PostVisibility.choices,
        default=PostVisibility.PUBLIC
    )
    
    # Reply/thread information
    reply_to_post = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    reply_to_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='mentioned_in_replies'
    )
    thread_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Retweet/quote information
    original_post = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='retweets'
    )
    quote_comment = models.TextField(
        max_length=280,
        null=True,
        blank=True,
        validators=[MaxLengthValidator(280)]
    )
    
    # Engagement metrics (denormalized for performance)
    likes_count = models.PositiveIntegerField(default=0)
    retweets_count = models.PositiveIntegerField(default=0)
    replies_count = models.PositiveIntegerField(default=0)
    quote_tweets_count = models.PositiveIntegerField(default=0)
    
    # Post metadata
    is_pinned = models.BooleanField(default=False)
    is_sensitive = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default='en')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'posts'
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['post_type', '-created_at']),
            models.Index(fields=['reply_to_post']),
            models.Index(fields=['original_post']),
            models.Index(fields=['thread_id']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['visibility', '-created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(likes_count__gte=0),
                name='positive_likes_count'
            ),
            models.CheckConstraint(
                check=models.Q(retweets_count__gte=0),
                name='positive_retweets_count'
            ),
        ]
    
    def __str__(self):
        return f"Post by @{self.author.username}: {self.content[:50]}..."
    
    def save(self, *args, **kwargs):
        # Set thread_id for replies
        if self.post_type == self.PostType.REPLY and self.reply_to_post:
            if not self.thread_id:
                self.thread_id = self.reply_to_post.thread_id or self.reply_to_post.id
        
        super().save(*args, **kwargs)


class Follow(models.Model):
    """Follow relationship between users."""
    
    class FollowStatus(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PENDING = 'pending', 'Pending'
        BLOCKED = 'blocked', 'Blocked'
        MUTED = 'muted', 'Muted'
    
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following_set'
    )
    followed = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers_set'
    )
    status = models.CharField(
        max_length=20,
        choices=FollowStatus.choices,
        default=FollowStatus.ACTIVE
    )
    
    # Follow metadata
    notifications_enabled = models.BooleanField(default=True)
    show_retweets = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'follows'
        unique_together = ['follower', 'followed']
        indexes = [
            models.Index(fields=['follower', 'status']),
            models.Index(fields=['followed', 'status']),
            models.Index(fields=['created_at']),
        ]
        constraints = [
            models.CheckConstraint(
                check=~models.Q(follower=models.F('followed')),
                name='no_self_follow'
            ),
        ]
    
    def __str__(self):
        return f"@{self.follower.username} follows @{self.followed.username}"


class Like(models.Model):
    """Like relationship between users and posts."""
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'likes'
        unique_together = ['user', 'post']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['post', '-created_at']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"@{self.user.username} likes post {self.post.id}"


class MediaAttachment(models.Model):
    """Media attachments for posts."""
    
    class MediaType(models.TextChoices):
        IMAGE = 'image', 'Image'
        VIDEO = 'video', 'Video'
        GIF = 'gif', 'GIF'
    
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='media_attachments'
    )
    media_type = models.CharField(
        max_length=10,
        choices=MediaType.choices
    )
    url = models.URLField()
    thumbnail_url = models.URLField(blank=True, null=True)
    alt_text = models.TextField(max_length=420, blank=True, null=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'media_attachments'
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['media_type']),
        ]
    
    def __str__(self):
        return f"{self.media_type} attachment for post {self.post.id}"


class Hashtag(models.Model):
    """Hashtag model for trending topics."""
    
    name = models.CharField(max_length=100, unique=True)
    posts = models.ManyToManyField(Post, through='PostHashtag', related_name='hashtags')
    
    # Trending metrics
    usage_count = models.PositiveIntegerField(default=0)
    trending_score = models.FloatField(default=0.0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hashtags'
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['-trending_score']),
            models.Index(fields=['-usage_count']),
        ]
    
    def __str__(self):
        return f"#{self.name}"


class PostHashtag(models.Model):
    """Many-to-many relationship between posts and hashtags."""
    
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    hashtag = models.ForeignKey(Hashtag, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'post_hashtags'
        unique_together = ['post', 'hashtag']
        indexes = [
            models.Index(fields=['post']),
            models.Index(fields=['hashtag']),
        ]
