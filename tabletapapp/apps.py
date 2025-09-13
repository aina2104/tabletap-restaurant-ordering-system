"""
apps.py

Configures the Django application for the "tabletapapp" module.

This file defines the application configuration class that Django uses
at startup to register app-specific settings and behaviors.
"""

from django.apps import AppConfig


class TabletapappConfig(AppConfig):
    """
    Application configuration for the Tabletapapp Django app.

    Attributes:
        default_auto_field (str): The type of auto-generated primary key field.
        name (str): The full Python path to the application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tabletapapp'
