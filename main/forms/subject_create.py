from django import forms
from django.core.exceptions import ValidationError

from main.models import (
    Discipline, Curriculum, Program, Faculty, University,
    Teaching, Teacher, StudentGroup
)

CONTROL_CHOICES = [("exam", "Экзамен"), ("test", "Зачет"), ("diff_test", "Дифф. зачет")]
SEMESTER_IN_YEAR = [(1, "осенний"), (2, "весенний")]


class DisciplineCreateForm(forms.ModelForm):
    class Meta:
        model = Discipline
        fields = ["code", "title", "ects"]
        labels = {"code": "Код", "title": "Название", "ects": "ECTS (час.)"}


class CurriculumCreateForm(forms.ModelForm):
    class Meta:
        model = Curriculum
        fields = ["program", "discipline", "semester", "hours", "control_form"]
        labels = {
            "program": "Программа (кафедра)",
            "discipline": "Дисциплина",
            "semester": "Семестр (1–12)",
            "hours": "Часы",
            "control_form": "Форма контроля",
        }

    def __init__(self, *args, **kwargs):
        university: University = kwargs.pop("university", None)
        super().__init__(*args, **kwargs)

        if university is not None:
            self.fields["program"].queryset = Program.objects.filter(
                faculty__university=university
            ).select_related("faculty").order_by("faculty__name", "name")

        self.fields["control_form"].widget = forms.Select(choices=CONTROL_CHOICES)

    def clean_semester(self):
        s = self.cleaned_data["semester"]
        if not (1 <= s <= 12):
            raise ValidationError("Семестр должен быть в диапазоне 1..12.")
        return s


class TeachingCreateForm(forms.ModelForm):
    class Meta:
        model = Teaching
        fields = ["teacher", "curriculum", "group", "academic_year", "semester_in_year"]
        labels = {
            "teacher": "Преподаватель",
            "curriculum": "Учебный план (Curriculum)",
            "group": "Группа (опционально, для потока — оставьте пустым)",
            "academic_year": "Учебный год (например, 2025-2026)",
            "semester_in_year": "Семестр в году",
        }

    def __init__(self, *args, **kwargs):
        university: University = kwargs.pop("university", None)
        super().__init__(*args, **kwargs)

        if university is not None:
            self.fields["teacher"].queryset = Teacher.objects.filter(
                university=university
            ).select_related("person").order_by("person__last_name", "person__first_name")

            self.fields["group"].queryset = StudentGroup.objects.filter(
                university=university
            ).order_by("name")

            self.fields["curriculum"].queryset = Curriculum.objects.filter(
                program__faculty__university=university
            ).select_related("program", "discipline").order_by("program__name", "discipline__title")

        self.fields["semester_in_year"].widget = forms.Select(choices=SEMESTER_IN_YEAR)

    def clean(self):
        cleaned = super().clean()
        teacher: Teacher = cleaned.get("teacher")
        group: StudentGroup = cleaned.get("group")
        curriculum: Curriculum = cleaned.get("curriculum")

        if teacher and group and teacher.university_id != group.university_id:
            self.add_error("group", "Группа и преподаватель должны относиться к одному университету.")

        if group and curriculum and group.program.faculty_id != curriculum.program.faculty_id:
            self.add_error("group", "Группа должна принадлежать тому же факультету/программе, что и curriculum.")

        if teacher and curriculum and teacher.university_id != curriculum.program.faculty.university_id:
            self.add_error("teacher", "Преподаватель и curriculum должны относиться к одному университету.")

        return cleaned