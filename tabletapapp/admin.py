"""
admin.py

Configures the Django admin interface for custom models, including:
- A custom UserAdmin that adds “Archive”/“Unarchive” actions.
- Registration of the Owner, Restaurant, Menu, Order, and related models.
"""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Import all models
from .models import *

User = get_user_model()

# First, unregister the default User admin so we can replace it
admin.site.unregister(User)


@admin.action(description="Archive users (disable login)")
def archive_users(modeladmin, request, queryset):
    """
    Mark selected User instances as inactive, preventing them from logging in.
    """
    queryset.update(is_active=False)


@admin.action(description="Unarchive users (enable login)")
def unarchive_users(modeladmin, request, queryset):
    """
    Mark selected User instances as active, allowing them to log in again.
    """
    queryset.update(is_active=True)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Customizes the admin display for the User model to include:
    - Bulk “Archive” and “Unarchive” actions.
    - An “Archived” column that inverts is_active.
    """
    actions = [archive_users, unarchive_users]
    # Extend the default list display and filters
    list_display = BaseUserAdmin.list_display + ('archived',)
    list_filter  = BaseUserAdmin.list_filter  + ('is_active',)

    @admin.display(boolean=True, description='Archived')
    def archived(self, obj):
        """
        Returns True when the user is archived (i.e., is_active is False).
        Displayed as a checkbox in the list view.
        """
        return not obj.is_active

# Register the models with default configurations:
admin.site.register(Owner)
admin.site.register(Restaurant)
admin.site.register(Restaurant_Owner)
admin.site.register(Menu)
admin.site.register(Menu_Category)
admin.site.register(Menu_Item)
admin.site.register(Order)
admin.site.register(Order_Item)
admin.site.register(Table)
