"""
Custom DRF permission classes.

IsAuthenticated  – request.user must be a register_model instance
                   (set by TokenAuthentication)
IsAdminUser      – same, plus user.is_admin must be True
"""

from rest_framework.permissions import BasePermission


class IsAuthenticated(BasePermission):
    """Allow access only to token-authenticated users."""
    message = "Authentication required. Provide a valid token."

    def has_permission(self, request, view):
        return bool(
            request.user and
            hasattr(request.user, 'Username')  # it's a register_model instance
        )


class IsAdminUser(BasePermission):
    """Allow access only to users with is_admin=True."""
    message = "Admin access required."

    def has_permission(self, request, view):
        return bool(
            request.user and
            hasattr(request.user, 'Username') and
            getattr(request.user, 'is_admin', False)
        )
