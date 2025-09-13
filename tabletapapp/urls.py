"""
urls.py

Defines URL routing for the Tabletap application, mapping URL patterns to corresponding view functions and class-based views.

Routes include owner-facing management (restaurants, menus, categories, items), authentication, and customer-facing ordering flows (QR code, menu browsing, cart, order viewing).
"""

from django.urls import include, path
from . import views
from .views import *

urlpatterns = [
    # Landing page
    path("", views.landing_page, name='landing_page'),

    # User authentication (django-allauth)
    path('accounts/', include('allauth.urls')),

    # Owner profile page
    path("profile/", views.profile_view, name='profile'),

    # Restaurant management
    path("restaurant/add/", views.add_restaurant, name='add_restaurant'),
    path("restaurant/<int:pk>/edit/", RestaurantUpdateView.as_view(), name='edit_restaurant'),

    # Menu management under a restaurant
    path('restaurant/<int:restaurant_id>/menu/add/', views.add_menu, name='add_menu'),
    path('restaurant/<int:pk>/menu/update/', MenuUpdateView.as_view(), name='update_menu'),
    path('restaurant/menu/<int:pk>/delete/', MenuDeleteView.as_view(), name='delete_menu'),

    # QR code generation for restaurant tables
    path('restaurant/<int:restaurant_id>/qr-code/', views.qr_code, name='qr_code'),

    # Owner dashboard: view menus and categories
    path("menu/<int:menu_id>/<int:category_id>/", views.dashboard, name='owner_menu'),
    path("menu/<int:menu_id>/category/add/", views.add_category, name='add_category'),
    path("menu/<int:menu_id>/category/<int:pk>/update/", CategoryUpdateView.as_view(), name='update_category'),
    path("menu/category/<int:pk>/delete/", CategoryDeleteView.as_view(), name='delete_category'),

    # Menu item management
    path("menu/<int:menu_id>/<int:category_id>/item/add/", views.add_menu_item, name='add_item'),
    path("menu/<int:menu_id>/<int:category_id>/item/<int:pk>/update/", MenuItemUpdateView.as_view(), name='update_item'),
    path("menu/<int:menu_id>/<int:category_id>/item/<int:pk>/delete/", ItemDeleteView.as_view(), name='delete_item'),

    # QR code namespace (external app for QR code routes)
    path("qr_code/", include('qr_code.urls', namespace="qr_code")),

    # Viewing current orders
    path("current_orders/<int:order_id>/", views.view_order, name="view_order"),

    # Customer ordering flow via QR code link
    path("customer/<int:table_id>/menu/<int:menu_id>/<int:category_id>/", views.customer_menu, name='customer_menu'),
    path("customer/<int:table_id>/<int:restaurant_id>/all/", views.all_menus, name='all_menus'),
    path("customer/<int:table_id>/menu/<int:menu_id>/item/<int:item_id>/add/", views.add_order_item, name='add_order_item'),
    path("customer/<int:table_id>/<int:restaurant_id>/menu/<int:menu_id>/cart/", views.view_cart, name='view_cart'),
]
