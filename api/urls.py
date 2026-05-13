"""
URL configuration for the Sprinkled Magic REST API.

All routes are prefixed with /api/ in the project urls.py.

Auth
    POST   /api/auth/register/
    POST   /api/auth/login/
    POST   /api/auth/logout/
    GET    /api/auth/me/

Products
    GET    /api/products/
    POST   /api/products/
    GET    /api/products/<id>/
    PUT    /api/products/<id>/
    PATCH  /api/products/<id>/
    DELETE /api/products/<id>/

Orders
    GET    /api/orders/
    POST   /api/orders/
    GET    /api/orders/<order_id>/
    PATCH  /api/orders/<order_id>/status/
"""

from django.urls import path
from . import views

urlpatterns = [
    # ── Auth ──────────────────────────────────────────────────────────────
    path('auth/register/', views.RegisterView.as_view(),  name='api_register'),
    path('auth/login/',    views.LoginView.as_view(),     name='api_login'),
    path('auth/logout/',   views.LogoutView.as_view(),    name='api_logout'),
    path('auth/me/',       views.MeView.as_view(),        name='api_me'),

    # ── Products ──────────────────────────────────────────────────────────
    path('products/',      views.ProductListView.as_view(),   name='api_products'),
    path('products/<int:pk>/', views.ProductDetailView.as_view(), name='api_product_detail'),

    # ── Orders ────────────────────────────────────────────────────────────
    path('orders/',        views.OrderListView.as_view(),  name='api_orders'),
    path('orders/<str:order_id>/',        views.OrderDetailView.as_view(), name='api_order_detail'),
    path('orders/<str:order_id>/status/', views.OrderStatusView.as_view(), name='api_order_status'),
]
