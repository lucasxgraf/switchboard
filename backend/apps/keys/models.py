import hashlib
import hmac
import secrets
import uuid

from django.conf import settings
from django.db import models


class ApiKey(models.Model):
    name = models.CharField(max_length=255, unique=True)
    prefix = models.CharField(max_length=255, unique=True)
    hash = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    rate_limit_per_minute = models.IntegerField(default=100)
    monthly_budget_micro_cents = models.IntegerField(default=500000000)
    last_used_at = models.DateTimeField(null=True, blank=True)
    raw_key: str

    def __str__(self) -> str:
        return self.name

    @classmethod
    def generate_key(cls, name: str) -> ApiKey:
        raw_key = f"sk-{secrets.token_urlsafe(32)}"
        prefix = raw_key[:11]
        digest = hmac.new(
            settings.API_KEY_HASH_SECRET.encode(), raw_key.encode(), hashlib.sha256
        ).hexdigest()
        instance = cls.objects.create(name=name, prefix=prefix, hash=digest)
        instance.raw_key = raw_key
        return instance


class RequestLog(models.Model):
    api_key = models.ForeignKey(ApiKey, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    requested_model = models.CharField(max_length=255)
    used_model = models.CharField(max_length=255)
    provider = models.CharField(max_length=255)
    prompt_tokens = models.IntegerField(null=True)
    completion_tokens = models.IntegerField(null=True)
    cost_micro_cents = models.IntegerField(null=True)
    gateway_latency_ms = models.IntegerField(null=True)
    provider_latency_ms = models.IntegerField(null=True)
    status_code = models.IntegerField()
    error_code = models.CharField(max_length=255)
    cache_hit = models.BooleanField(default=False)
    streaming = models.BooleanField(default=False)
    fallback_depth = models.IntegerField(default=0)
    request_id = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)

    def __str__(self) -> str:
        return f"RequestLog {self.request_id} for API Key {self.api_key.name}"
