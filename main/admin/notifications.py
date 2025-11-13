from django import forms
from django.contrib import admin
from django.utils.html import format_html

from main.models import GroupNotification


class GroupNotificationForm(forms.ModelForm):
    class Meta:
        model = GroupNotification
        fields = "__all__"

    def clean(self):
        cleaned = super().clean()
        uni = cleaned.get("university")
        group = cleaned.get("group")
        if uni and group and group.university_id != uni.id:
            self.add_error("group", "Группа должна относиться к тому же университету.")
        return cleaned


@admin.register(GroupNotification)
class GroupNotificationAdmin(admin.ModelAdmin):
    form = GroupNotificationForm

    list_display = (
        "icon_display",
        "short_text",
        "group",
        "university",
        "sender",
        "created_at",
    )
    list_display_links = ("short_text",)
    list_select_related = ("group", "university", "sender")

    list_filter = (
        ("university", admin.RelatedOnlyFieldListFilter),
        ("group", admin.RelatedOnlyFieldListFilter),
        ("group__program", admin.RelatedOnlyFieldListFilter),
        "created_at",
    )

    search_fields = (
        "text",
        "group__name",
        "sender__last_name",
        "sender__first_name",
        "sender__middle_name",
    )

    autocomplete_fields = ("university", "group", "sender")

    date_hierarchy = "created_at"
    readonly_fields = ("created_at",)
    ordering = ("-created_at",)

    fieldsets = (
        (None, {
            "fields": (
                ("university", "group"),
                "sender",
                ("icon",),
                "text",
            )
        }),
        ("Служебное", {
            "classes": ("collapse",),
            "fields": ("created_at",),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("group", "university", "sender")

    def icon_display(self, obj):
        return format_html('<span style="font-size:1.1rem;">{}</span>', obj.icon or "🔔")
    icon_display.short_description = "Иконка"

    def short_text(self, obj):
        txt = obj.text or ""
        return (txt[:80] + "…") if len(txt) > 80 else txt
    short_text.short_description = "Текст"