from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime

from ..models import Person, Student, University, StudentGroup, Role

class StudentCreateForm(forms.Form):
    university = forms.ModelChoiceField(
        queryset=University.objects.all(),
        label="Университет",
    )
    student_group = forms.ModelChoiceField(
        queryset=StudentGroup.objects.all(),
        label="Студенческая группа",
    )
    student_id = forms.CharField(
        label="Номер студенческого билета",
        max_length=32,
        widget=forms.TextInput(attrs={'pattern': '[0-9]+', 'title': 'Только цифры'})
    )
    current_year = forms.IntegerField(
        label="Текущий курс",
        min_value=1,
        max_value=6,
        help_text="Курс (1..6)",
        widget=forms.NumberInput(attrs={'min': '1', 'max': '6'})
    )
    admission_year = forms.IntegerField(
        label="Год поступления",
        widget=forms.NumberInput(attrs={'type': 'number', 'min': '2000', 'max': str(datetime.now().year + 1)})
    )

    def __init__(self, *args, **kwargs):
        self.person = kwargs.pop("person", None)
        super().__init__(*args, **kwargs)

        if self.person is None:
            raise ValueError("StudentCreateForm требует параметр 'person'")

        # Фильтруем группы по университету, если выбран
        if 'university' in self.data:
            try:
                university_id = int(self.data.get('university'))
                self.fields['student_group'].queryset = StudentGroup.objects.filter(university_id=university_id)
            except (ValueError, TypeError):
                pass

    def clean_student_id(self):
        student_id = self.cleaned_data["student_id"]
        if not student_id.isdigit():
            raise ValidationError("Номер студенческого билета должен состоять только из цифр.")
        if Student.objects.filter(student_id=student_id).exists():
            raise ValidationError("Студенческий билет с таким номером уже существует.")
        return student_id

    def clean_admission_year(self):
        admission_year = self.cleaned_data["admission_year"]
        current_year = datetime.now().year
        if admission_year < 2000 or admission_year > current_year + 1:
            raise ValidationError(f"Год поступления должен быть между 2000 и {current_year + 1}.")
        return admission_year

    def clean(self):
        cleaned_data = super().clean()
        university = cleaned_data.get("university")
        student_group = cleaned_data.get("student_group")

        if university and student_group and student_group.university != university:
            raise ValidationError("Выбранная группа не принадлежит выбранному университету.")

        if hasattr(self.person, "student"):
            raise ValidationError("У этого человека уже есть роль Student.")

        return cleaned_data

    def save(self):
        university = self.cleaned_data["university"]
        student_group = self.cleaned_data["student_group"]
        student_id = self.cleaned_data["student_id"]
        current_year = self.cleaned_data["current_year"]
        admission_year = self.cleaned_data["admission_year"]

        student = Student.objects.create(
            person=self.person,
            university=university,
            student_group=student_group,
            student_id=student_id,
            current_year=current_year,
            admission_year=admission_year,
        )

        student_role, _ = Role.objects.get_or_create(permission="Student", defaults={"name": "Студент"})
        self.person.role = student_role
        self.person.save(update_fields=["role"])

        return student
