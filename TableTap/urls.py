"""
URL configuration for the Django project.

This file defines the URL routing for the project, mapping URL paths to views or including other URL configurations.

- 'admin/': Django admin interface.
- '': Includes URL patterns from the 'tabletapapp' application as the main app.
- '': Includes URL patterns from the 'qr_code' package with namespace support.

It also imports necessary modules for admin, authentication views, and static/media file handling (used in development if configured).
"""

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from tabletapapp import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("tabletapapp.urls")),
    path('', include('qr_code.urls', namespace='qr_code')),
]
