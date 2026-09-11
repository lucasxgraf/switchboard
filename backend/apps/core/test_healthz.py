from django.test import TestCase
from django.urls import reverse
from rest_framework import status


class CoreHealthCheckTestCase(TestCase):
    def test_health_check(self) -> None:
        url = reverse("health_check")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertEqual(response.json(), {"status": "ok"})
