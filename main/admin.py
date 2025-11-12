from django.contrib import admin
from django.db.models import Q, F
from django.utils import timezone
from django.utils.html import format_html
from .models import ApplicationRequest
from django import forms

from .models import (
    Person, Teacher, StudentGroup, Student,
    University, Faculty, Program, Discipline, Curriculum, Teaching,
    Role, StudentRole,
    Enrollment, Assessment, AssessmentResult,
    StudentRequest, TeacherRequest,
    Applicant, ApplicantExam, AdmissionRequest,
    NewsPost, ScheduleSlot, ScheduleException,
    GroupNotification
)

# ===============================
#  Общие настройки админки
# ===============================

admin.site.site_header = "Цифровой кампус — админпанель"
admin.site.site_title = "Цифровой кампус"
admin.site.index_title = "Управление данными"


# ===============================
#  Инлайны
# ===============================

class StudentRoleInline(admin.TabularInline):
    model = StudentRole
    extra = 0
    autocomplete_fields = ("student",)
    fields = ("role", "start_date", "end_date")
    show_change_link = True


class EnrollmentInline(admin.TabularInline):
    model = Enrollment
    extra = 0
    autocomplete_fields = ("student", "teaching")
    fields = ("student", "teaching", "is_active", "date_enrolled")
    readonly_fields = ("date_enrolled",)
    show_change_link = True


class AssessmentInline(admin.TabularInline):
    model = Assessment
    extra = 0
    fields = ("title", "type", "max_points", "weight", "due_at", "is_final")
    show_change_link = True


class AssessmentResultInline(admin.TabularInline):
    model = AssessmentResult
    extra = 0
    autocomplete_fields = ("student",)
    fields = ("student", "attempt", "points", "graded_at", "grade_5", "grade_ects")
    readonly_fields = ("graded_at",)
    show_change_link = True


class ApplicantExamInline(admin.TabularInline):
    model = ApplicantExam
    extra = 0
    fields = ("subject", "exam_type", "score")
    show_change_link = True


class AdmissionRequestInline(admin.TabularInline):
    model = AdmissionRequest
    extra = 0
    autocomplete_fields = ("program",)
    fields = ("program", "priority", "status", "submitted_at")
    readonly_fields = ("submitted_at",)
    show_change_link = True

class TeachingInline(admin.TabularInline):
    model = Teaching
    extra = 0
    autocomplete_fields = ("curriculum", "group")
    fields = ("curriculum", "group", "academic_year", "semester_in_year")
    show_change_link = True

class ScheduleExceptionInline(admin.TabularInline):
    model = ScheduleException
    extra = 0
    fields = (
        "date", "action",
        "new_date", "new_start_time", "new_end_time",
        "new_building", "new_room", "new_note",
        "created_at",
    )
    readonly_fields = ("created_at",)
    classes = ("collapse",)

# ===============================
#  Университетские структуры
# ===============================

@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    list_display = ("short_name", "name", "city", "contact_email")
    search_fields = ("name", "short_name", "city", "contact_email")
    ordering = ("short_name",)


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ("name", "university")
    list_filter = ("university",)
    search_fields = ("name", "university__name", "university__short_name")
    autocomplete_fields = ("university",)


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "faculty", "duration_years")
    list_filter = ("faculty__university", "faculty")
    search_fields = ("name", "code", "faculty__name", "faculty__university__name")
    autocomplete_fields = ("faculty",)
    ordering = ("faculty", "name")


@admin.register(Discipline)
class DisciplineAdmin(admin.ModelAdmin):
    list_display = ("title", "code", "ects")
    search_fields = ("title", "code")


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = ("program", "discipline", "semester", "hours", "control_form")
    list_filter = ("program__faculty__university", "program__faculty", "program", "semester", "control_form")
    search_fields = ("program__name", "discipline__title", "discipline__code")
    autocomplete_fields = ("program", "discipline")
    ordering = ("program", "semester")


# ===============================
#  Люди и связанное
# ===============================

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "permission")
    list_filter = ("permission",)
    search_fields = ("name", "permission")


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "middle_name", "email", "phone", "vk_user_id", "role")
    search_fields = ("last_name", "first_name", "middle_name", "email", "phone", "vk_user_id")
    list_filter = ("role__permission",)
    autocomplete_fields = ("user", "role")
    ordering = ("last_name", "first_name")

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("person", "department", "academic_title", "university")
    list_filter = ("university", "department")
    search_fields = ("person__last_name", "person__first_name", "department", "academic_title")
    autocomplete_fields = ("person", "university")
    inlines = [TeachingInline]


@admin.register(StudentGroup)
class StudentGroupAdmin(admin.ModelAdmin):
    list_display = ("name", "program", "admission_year", "university", "curator")
    list_filter = ("university", "program__faculty", "program", "admission_year")
    search_fields = ("name", "program__name", "program__faculty__name", "university__name", "curator__person__last_name")
    autocomplete_fields = ("university", "program", "curator")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("person", "student_id", "student_group", "university", "current_year", "admission_year")
    list_filter = ("university", "student_group__program__faculty", "student_group", "current_year", "admission_year")
    search_fields = ("person__last_name", "person__first_name", "student_id", "student_group__name")
    autocomplete_fields = ("person", "university", "student_group")
    inlines = [StudentRoleInline, EnrollmentInline]
    ordering = ("person__last_name",)


# ===============================
#  Учебный процесс
# ===============================

@admin.register(Teaching)
class TeachingAdmin(admin.ModelAdmin):
    list_display = ("teacher", "curriculum", "group", "academic_year", "semester_in_year")
    list_filter = ("teacher__university", "academic_year", "semester_in_year", "group", "curriculum__program")
    search_fields = ("teacher__person__last_name", "curriculum__discipline__title", "group__name", "academic_year")
    autocomplete_fields = ("teacher", "curriculum", "group")
    inlines = [AssessmentInline, EnrollmentInline]
    ordering = ("-academic_year", "teacher")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "teaching", "is_active", "date_enrolled")
    list_filter = ("is_active", "teaching__academic_year", "teaching__semester_in_year", "teaching__teacher__university")
    search_fields = ("student__person__last_name", "teaching__curriculum__discipline__title", "teaching__group__name")
    autocomplete_fields = ("student", "teaching")
    date_hierarchy = "date_enrolled"


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("title", "teaching", "type", "max_points", "weight", "due_at", "is_final")
    list_filter = ("type", "is_final", "teaching__academic_year", "teaching__semester_in_year")
    search_fields = ("title", "teaching__curriculum__discipline__title", "teaching__teacher__person__last_name")
    autocomplete_fields = ("teaching",)
    inlines = [AssessmentResultInline]
    date_hierarchy = "due_at"


@admin.register(AssessmentResult)
class AssessmentResultAdmin(admin.ModelAdmin):
    list_display = ("assessment", "student", "attempt", "points", "grade_5", "grade_ects", "graded_at")
    list_filter = ("assessment__type", "grade_5", "grade_ects", "graded_at")
    search_fields = ("assessment__title", "student__person__last_name", "student__student_id")
    autocomplete_fields = ("assessment", "student")
    readonly_fields = ("graded_at",)
    date_hierarchy = "graded_at"


# ===============================
#  Заявления
# ===============================

@admin.register(StudentRequest)
class StudentRequestAdmin(admin.ModelAdmin):
    list_display = ("student", "university", "type", "status", "created_at", "updated_at")
    list_filter = ("university", "type", "status", "created_at")
    search_fields = ("student__person__last_name", "student__student_id")
    autocomplete_fields = ("university", "student")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"


@admin.register(TeacherRequest)
class TeacherRequestAdmin(admin.ModelAdmin):
    list_display = ("teacher", "university", "type", "status", "created_at", "updated_at")
    list_filter = ("university", "type", "status", "created_at")
    search_fields = ("teacher__person__last_name", "teacher__department")
    autocomplete_fields = ("university", "teacher")
    readonly_fields = ("created_at", "updated_at")
    date_hierarchy = "created_at"


# ===============================
#  Абитуриенты
# ===============================

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ("person", "birth_date", "school_name", "graduation_year", "linked_student")
    search_fields = ("person__last_name", "person__first_name", "school_name", "passport_number")
    autocomplete_fields = ("person", "linked_student")
    inlines = [ApplicantExamInline, AdmissionRequestInline]


@admin.register(ApplicantExam)
class ApplicantExamAdmin(admin.ModelAdmin):
    list_display = ("applicant", "subject", "exam_type", "score")
    list_filter = ("exam_type",)
    search_fields = ("applicant__person__last_name", "subject")
    autocomplete_fields = ("applicant",)


@admin.register(AdmissionRequest)
class AdmissionRequestAdmin(admin.ModelAdmin):
    list_display = ("applicant", "program", "priority", "status", "submitted_at")
    list_filter = ("status", "priority", "program__faculty__university", "program__faculty")
    search_fields = ("applicant__person__last_name", "program__name", "program__code")
    autocomplete_fields = ("applicant", "program")
    readonly_fields = ("submitted_at",)
    date_hierarchy = "submitted_at"


# ===============================
#  Новости
# ===============================

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

# ===============================
#  Расписание
# ===============================

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


@admin.register(ApplicationRequest)
class ApplicationRequestAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'email', 'desired_program', 'study_form', 'status', 'created_at']
    list_filter = ['study_form', 'status', 'created_at']
    search_fields = ['last_name', 'first_name', 'email', 'desired_program']
    readonly_fields = ['created_at']

    fieldsets = (
        ('Личные данные', {
            'fields': ('last_name', 'first_name', 'middle_name', 'email', 'phone')
        }),
        ('Информация о поступлении', {
            'fields': ('desired_program', 'study_form', 'previous_education', 'comments')
        }),
        ('Системная информация', {
            'fields': ('status', 'created_at')
        }),
    )

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
