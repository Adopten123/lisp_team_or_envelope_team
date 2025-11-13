from django.contrib import admin

from main.models import University, Faculty, Program, Discipline, Curriculum


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