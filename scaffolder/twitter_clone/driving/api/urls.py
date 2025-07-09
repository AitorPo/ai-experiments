"""
Main API URL configuration.
"""

from django.urls import path, include

urlpatterns = [
    path("v1/", include("driving.api.v1.urls")),
]
