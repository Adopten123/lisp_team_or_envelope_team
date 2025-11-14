from django.contrib import admin

from main.models import Applicant, ApplicantExam, AdmissionRequest, ApplicationRequest
from .inlines import ApplicantExamInline


@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ("person", "birth_date", "school_name", "graduation_year", "linked_student")
    search_fields = ("person__last_name", "person__first_name", "school_name", "passport_number")
    autocomplete_fields = ("person", "linked_student")


@admin.register(ApplicantExam)
class ApplicantExamAdmin(admin.ModelAdmin):
    list_display = ("applicant", "subject", "exam_type", "score")
    list_filter = ("exam_type",)
    search_fields = ("applicant__person__last_name", "subject")
    autocomplete_fields = ("applicant",)


@admin.register(ApplicationRequest)
class ApplicationRequestAdmin(admin.ModelAdmin):
    list_display = ["last_name", "first_name", "email", "desired_program", "study_form", "status", "created_at"]
    list_filter = ["study_form", "status", "created_at"]
    search_fields = ["last_name", "first_name", "email", "desired_program"]
    readonly_fields = ["created_at"]

    fieldsets = (
        ("Личные данные", {
            "fields": ("last_name", "first_name", "middle_name", "email", "phone")
        }),
        ("Информация о поступлении", {
            "fields": ("desired_program", "study_form", "previous_education", "comments")
        }),
        ("Системная информация", {
            "fields": ("status", "created_at")
        }),
    )
