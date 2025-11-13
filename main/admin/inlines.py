from django.contrib import admin

from main.models import (
    StudentRole,
    Enrollment,
    Assessment,
    AssessmentResult,
    ApplicantExam,
    Teaching,
    ScheduleException,
)


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
