from django.test import TestCase, override_settings
from django.urls import path
from rest_framework import status
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.test import APIClient
from rest_framework.views import APIView

from .authentication import ApiKeyAuthentication


class ProbeView(APIView):
    authentication_classes = [ApiKeyAuthentication]

    def get(self, request: Request) -> Response:
        return Response({"api_key_name": request.api_key.name})


urlpatterns = [path("probe/", ProbeView.as_view())]


@override_settings(ROOT_URLCONF=__name__)
class ApiKeyAuthenticationTestCase(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_missing_header_declined(self) -> None:
        response = self.client.get("/probe/")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_malformed_header_declined(self) -> None:
        response = self.client.get(
            "/probe/", HTTP_AUTHORIZATION="sk-irgendwas-ohne-bearer-prefix"
        )

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_unknown_key_declined(self) -> None:
        pass

    def test_valid_key_authenticates(self) -> None:
        pass
