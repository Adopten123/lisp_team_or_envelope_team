from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from main.models import NewsPost


@admin.register(NewsPost)
class NewsPostAdmin(admin.ModelAdmin):
    list_display = ("title", "news_icon", "university", "is_published", "published_at", "author", "cover_thumb")
    list_filter = ("university", "is_published", "published_at")
    search_fields = ("title", "body", "author")
    autocomplete_fields = ("university",)
    readonly_fields = ("created_at",)
    date_hierarchy = "published_at"
    ordering = ("-published_at",)

    actions = ["publish_now", "unpublish"]
    fieldsets = (
        (None, {"fields": ("university", "news_icon", "title", "author", "is_published")}),
        ("Контент", {"fields": ("cover_image", "body")}),
        ("Даты", {"fields": ("created_at", "published_at")}),
    )

    @admin.display(description="Обложка")
    def cover_thumb(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" style="height:40px;border-radius:4px;" />', obj.cover_image.url)
        return "—"

    @admin.action(description="Опубликовать сейчас")
    def publish_now(self, request, queryset):
        n = queryset.update(is_published=True, published_at=timezone.now())
        self.message_user(request, f"Опубликовано: {n}")

    @admin.action(description="Снять с публикации")
    def unpublish(self, request, queryset):
        n = queryset.update(is_published=False)
        self.message_user(request, f"Снято с публикации: {n}")