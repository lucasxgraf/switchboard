from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from .models import ApiKey


class ApiKeyAuthentication(BaseAuthentication):
    def authenticate_header(self, request: Request) -> str:
        return "Bearer"

    def authenticate(self, request: Request) -> tuple[None, ApiKey] | None:
        header = request.headers.get("Authorization")
        if header is None:
            raise AuthenticationFailed("No Authorization header provided.")

        if not header.startswith("Bearer "):
            raise AuthenticationFailed("Invalid Authorization header format.")

        return None
