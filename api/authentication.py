"""
Simple token-based authentication for the Sprinkled Magic API.

A token is a 40-character hex string stored in the ApiToken table,
linked to a register_model user.  Clients send it as:

    Authorization: Token <token_value>
"""

import binascii
import os

from django.db import models
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from Application.models import register_model


# ---------------------------------------------------------------------------
# Token model  (lives in the 'api' app)
# ---------------------------------------------------------------------------

class ApiToken(models.Model):
    user       = models.OneToOneField(
        register_model, on_delete=models.CASCADE, related_name='api_token'
    )
    key        = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = binascii.hexlify(os.urandom(20)).decode()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Token for {self.user.Username}"

    @classmethod
    def get_or_create_for(cls, user):
        token, _ = cls.objects.get_or_create(user=user)
        return token.key


# ---------------------------------------------------------------------------
# DRF authentication backend
# ---------------------------------------------------------------------------

class TokenAuthentication(BaseAuthentication):
    """
    Reads the 'Authorization: Token <key>' header and returns
    (register_model_instance, token_key) when valid.
    """
    keyword = 'Token'

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith(self.keyword + ' '):
            return None  # Not our scheme — let other backends try

        token_key = auth_header[len(self.keyword) + 1:].strip()
        return self._authenticate_credentials(token_key)

    def _authenticate_credentials(self, token_key):
        try:
            token = ApiToken.objects.select_related('user').get(key=token_key)
        except ApiToken.DoesNotExist:
            raise AuthenticationFailed('Invalid or expired token.')
        return (token.user, token_key)

    def authenticate_header(self, request):
        return self.keyword
