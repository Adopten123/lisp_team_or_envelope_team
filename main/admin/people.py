from django.contrib import admin

from main.models import Role, Person, Teacher, StudentGroup, Student
from .inlines import StudentRoleInline, EnrollmentInline, TeachingInline


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
    search_fields = (
        "name",
        "program__name",
        "program__faculty__name",
        "university__name",
        "curator__person__last_name",
    )
    autocomplete_fields = ("university", "program", "curator")


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("person", "student_id", "student_group", "university", "current_year", "admission_year")
    list_filter = (
        "university",
        "student_group__program__faculty",
        "student_group",
        "current_year",
        "admission_year",
    )
    search_fields = ("person__last_name", "person__first_name", "student_id", "student_group__name")
    autocomplete_fields = ("person", "university", "student_group")
    inlines = [StudentRoleInline, EnrollmentInline]
    ordering = ("person__last_name",)