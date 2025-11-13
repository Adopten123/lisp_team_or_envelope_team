from django.contrib import admin

from main.models import Teaching, Enrollment, Assessment, AssessmentResult
from .inlines import AssessmentInline, EnrollmentInline, AssessmentResultInline


@admin.register(Teaching)
class TeachingAdmin(admin.ModelAdmin):
    list_display = ("teacher", "curriculum", "group", "academic_year", "semester_in_year")
    list_filter = ("teacher__university", "academic_year", "semester_in_year", "group", "curriculum__program")
    search_fields = (
        "teacher__person__last_name",
        "curriculum__discipline__title",
        "group__name",
        "academic_year",
    )
    autocomplete_fields = ("teacher", "curriculum", "group")
    inlines = [AssessmentInline, EnrollmentInline]
    ordering = ("-academic_year", "teacher")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "teaching", "is_active", "date_enrolled")
    list_filter = (
        "is_active",
        "teaching__academic_year",
        "teaching__semester_in_year",
        "teaching__teacher__university",
    )
    search_fields = (
        "student__person__last_name",
        "teaching__curriculum__discipline__title",
        "teaching__group__name",
    )
    autocomplete_fields = ("student", "teaching")
    date_hierarchy = "date_enrolled"


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ("title", "teaching", "type", "max_points", "weight", "due_at", "is_final")
    list_filter = ("type", "is_final", "teaching__academic_year", "teaching__semester_in_year")
    search_fields = (
        "title",
        "teaching__curriculum__discipline__title",
        "teaching__teacher__person__last_name",
    )
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