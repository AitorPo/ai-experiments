"""
Django app configuration for the database layer.
"""

from django.apps import AppConfig


class DbConfig(AppConfig):
    """Configuration for the database app."""
    
    default_auto_field = "django.db.models.BigAutoField"
    name = "driven.db"
    verbose_name = "Database Layer"
