from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.messages import get_messages
from django.test import RequestFactory, TestCase
from django.urls import reverse

from .admin import RequestLogAdmin
from .models import ApiKey, RequestLog

User = get_user_model()


class RequestLogAdminTestCase(TestCase):
    def test_read_only(self) -> None:
        admin_instance = RequestLogAdmin(RequestLog, admin.site)
        request = RequestFactory().get("/")

        self.assertFalse(admin_instance.has_add_permission(request))
        self.assertFalse(admin_instance.has_change_permission(request))
        self.assertFalse(admin_instance.has_delete_permission(request))


class ApiKeyAdminTestCase(TestCase):
    def setUp(self) -> None:
        superuser = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="x"
        )
        self.client.force_login(superuser)

    def test_add_shows_raw_key_once(self) -> None:
        response = self.client.post(
            reverse("admin:keys_apikey_add"), {"name": "SmokeTestKey"}
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(ApiKey.objects.filter(name="SmokeTestKey").exists())

        messages = [m.message for m in get_messages(response.wsgi_request)]
        self.assertTrue(any("sk-" in message for message in messages))
