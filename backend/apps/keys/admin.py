from django.contrib import admin, messages
from django.forms import ModelForm
from django.http import HttpRequest, HttpResponse

from .models import ApiKey, RequestLog


@admin.register(ApiKey)
class ApiKeyAdmin(admin.ModelAdmin):
    list_display = ["name", "prefix_display", "active", "created_at"]
    list_filter = ["active", "created_at"]
    search_fields = ["name"]
    readonly_fields = ["prefix_display", "created_at", "last_used_at"]
    exclude = ["hash"]

    def get_fields(self, request: HttpRequest, obj: ApiKey | None = None) -> list[str]:  # type: ignore[override]
        if obj is None:
            return ["name"]
        return [
            "name",
            "prefix_display",
            "active",
            "rate_limit_per_minute",
            "monthly_budget_micro_cents",
            "created_at",
            "last_used_at",
        ]

    def save_model(
        self, request: HttpRequest, obj: ApiKey, form: ModelForm, change: bool
    ) -> None:
        if change:
            obj.save()
            return

        generated = ApiKey.generate_key(name=obj.name)
        obj.pk = generated.pk
        obj.refresh_from_db()
        obj.raw_key = generated.raw_key

    def response_add(
        self, request: HttpRequest, obj: ApiKey, post_url_continue: str | None = None
    ) -> HttpResponse:
        if hasattr(obj, "raw_key"):
            self.message_user(
                request,
                f"API key (copy now, shown only once): {obj.raw_key}",
                level=messages.WARNING,
            )
        return super().response_add(request, obj, post_url_continue)

    @admin.display(description="Prefix")
    def prefix_display(self, obj: ApiKey) -> str:
        return f"{obj.prefix}..."


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "api_key",
        "requested_model",
        "used_model",
        "status_code",
        "timestamp",
    ]
    list_filter = ["provider", "status_code", "cache_hit", "streaming"]
    search_fields = ["api_key__name", "requested_model"]

    def has_add_permission(self, request: HttpRequest) -> bool:
        return False

    def has_change_permission(
        self, request: HttpRequest, obj: ApiKey | None = None
    ) -> bool:
        return False

    def has_delete_permission(
        self, request: HttpRequest, obj: ApiKey | None = None
    ) -> bool:
        return False
