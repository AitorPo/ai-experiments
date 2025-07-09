"""
Pytest configuration for hexagonal architecture tests.
"""

import pytest
from django.conf import settings
from django.test import TransactionTestCase
import django


def pytest_configure():
    """Configure Django settings for pytest."""
    if not settings.configured:
        settings.configure(
            **{
                'DATABASES': {
                    'default': {
                        'ENGINE': 'django.db.backends.sqlite3',
                        'NAME': ':memory:',
                    }
                },
                'INSTALLED_APPS': [
                    'django.contrib.contenttypes',
                    'django.contrib.auth',
                    'driven.db',
                ],
                'SECRET_KEY': 'test-secret-key',
                'USE_TZ': True,
            }
        )
        django.setup()


@pytest.fixture
def example_entity():
    """Fixture providing a test example entity."""
    from domain.entities.example import ExampleEntity
    return ExampleEntity(
        name="Test Example",
        description="A test example entity",
        is_active=True
    )


@pytest.fixture
def example_repository():
    """Fixture providing a test repository."""
    from driven.db.adapter import ExampleRepositoryAdapter
    return ExampleRepositoryAdapter()


@pytest.fixture
def example_service(example_repository):
    """Fixture providing a test service."""
    from application.services.example_service import ExampleService
    return ExampleService(example_repository)
