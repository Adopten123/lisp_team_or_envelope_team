from django import forms
from django.core.exceptions import ValidationError

from ..models import Person, Teacher, University, Role

class TeacherCreateForm(forms.Form):
    person = forms.ModelChoiceField(
        queryset=Person.objects.filter(teacher__isnull=True),
        label="Человек",
        help_text="Выберите Person без роли Teacher",
    )
    academic_title = forms.CharField(label="Учёное звание", max_length=128, required=False)
    department = forms.CharField(label="Кафедра", max_length=255, required=False)

    def clean_person(self):
        person = self.cleaned_data["person"]
        if hasattr(person, "teacher"):
            raise ValidationError("У этого человека уже есть роль Teacher.")
        return person

    def save(self, *, university):
        person = self.cleaned_data["person"]
        academic_title = self.cleaned_data.get("academic_title") or ""
        department = self.cleaned_data.get("department") or ""

        teacher = Teacher.objects.create(
            person=person,
            academic_title=academic_title,
            department=department,
            university=university,
        )

        teacher_role, _ = Role.objects.get_or_create(permission="Teacher", defaults={"name": "Учитель"})
        person.role = teacher_role
        person.save(update_fields=["role"])

        return teacher