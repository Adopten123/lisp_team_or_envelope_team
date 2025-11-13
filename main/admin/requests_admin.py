from django.contrib import admin

from main.models import StudentRequest, TeacherRequest


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