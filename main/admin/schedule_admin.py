from django.contrib import admin

from main.models import ScheduleSlot, ScheduleException
from .inlines import ScheduleExceptionInline


@admin.register(ScheduleSlot)
class ScheduleSlotAdmin(admin.ModelAdmin):
    inlines = [ScheduleExceptionInline]

    list_display = (
        "id",
        "university",
        "get_discipline",
        "get_teacher",
        "weekday",
        "start_time",
        "end_time",
        "week_parity",
        "date_range",
        "rooms",
        "groups_count",
    )
    list_select_related = (
        "university",
        "teaching",
        "teaching__teacher__person",
        "teaching__curriculum__discipline",
    )
    list_filter = (
        "university",
        "weekday",
        "week_parity",
        ("groups", admin.RelatedOnlyFieldListFilter),
        ("teaching__teacher", admin.RelatedOnlyFieldListFilter),
    )
    search_fields = (
        "note",
        "room",
        "building",
        "teaching__curriculum__discipline__title",
        "teaching__teacher__person__last_name",
        "teaching__teacher__person__first_name",
        "groups__name",
    )
    filter_horizontal = ("groups",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Привязки", {
            "fields": ("university", "teaching", "groups")
        }),
        ("Время", {
            "fields": ("weekday", ("start_time", "end_time"), "week_parity", ("start_date", "end_date"))
        }),
        ("Место", {
            "fields": (("building", "room"), "note")
        }),
        ("Служебное", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )
    ordering = ("weekday", "start_time")

    @admin.display(description="Дисциплина", ordering="teaching__curriculum__discipline__title")
    def get_discipline(self, obj: ScheduleSlot):
        return obj.teaching.curriculum.discipline.title

    @admin.display(description="Преподаватель", ordering="teaching__teacher__person__last_name")
    def get_teacher(self, obj: ScheduleSlot):
        return str(obj.teaching.teacher.person)

    @admin.display(description="Период")
    def date_range(self, obj: ScheduleSlot):
        return f"{obj.start_date:%d.%m.%Y} — {obj.end_date:%d.%m.%Y}"

    @admin.display(description="Аудитория")
    def rooms(self, obj: ScheduleSlot):
        if obj.building or obj.room:
            return f"{obj.building or ''} {obj.room or ''}".strip()
        return "—"

    @admin.display(description="Групп")
    def groups_count(self, obj: ScheduleSlot):
        return obj.groups.count()


@admin.register(ScheduleException)
class ScheduleExceptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "date",
        "action",
        "slot",
        "slot_university",
        "slot_weekday",
        "slot_time",
        "slot_discipline",
        "slot_teacher",
    )
    list_select_related = (
        "slot",
        "slot__university",
        "slot__teaching",
        "slot__teaching__teacher__person",
        "slot__teaching__curriculum__discipline",
    )
    list_filter = (
        "action",
        "date",
        ("slot__university", admin.RelatedOnlyFieldListFilter),
        "slot__weekday",
    )
    search_fields = (
        "slot__note",
        "slot__room",
        "slot__building",
        "slot__teaching__curriculum__discipline__title",
        "slot__teaching__teacher__person__last_name",
        "slot__teaching__teacher__person__first_name",
        "slot__groups__name",
    )
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Исключение", {
            "fields": ("slot", "date", "action")
        }),
        ("Новые параметры (для переноса/смены аудитории)", {
            "fields": ("new_date", ("new_start_time", "new_end_time"), ("new_building", "new_room"), "new_note")
        }),
        ("Служебное", {
            "classes": ("collapse",),
            "fields": ("created_at",),
        }),
    )
    ordering = ("-date", "-id")

    @admin.display(description="Университет", ordering="slot__university__name")
    def slot_university(self, obj: ScheduleException):
        return obj.slot.university

    @admin.display(description="День")
    def slot_weekday(self, obj: ScheduleException):
        return obj.slot.get_weekday_display()

    @admin.display(description="Время")
    def slot_time(self, obj: ScheduleException):
        s = obj.slot
        return f"{s.start_time}–{s.end_time}"

    @admin.display(description="Дисциплина", ordering="slot__teaching__curriculum__discipline__title")
    def slot_discipline(self, obj: ScheduleException):
        return obj.slot.teaching.curriculum.discipline.title

    @admin.display(description="Преподаватель", ordering="slot__teaching__teacher__person__last_name")
    def slot_teacher(self, obj: ScheduleException):
        return str(obj.slot.teaching.teacher.person)