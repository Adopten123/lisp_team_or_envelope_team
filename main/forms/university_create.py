from django import forms
from django.core.exceptions import ValidationError
from main.models import Faculty, Program, University

class FacultyCreateForm(forms.Form):
    name = forms.CharField(label="Название факультета", max_length=256)

    def save(self, *, university):
        return Faculty.objects.create(university=university, name=self.cleaned_data["name"])


class ProgramCreateForm(forms.Form):
    faculty = forms.ModelChoiceField(queryset=Faculty.objects.none(), label="Факультет")
    name = forms.CharField(label="Название кафедры/направления", max_length=255)
    code = forms.CharField(label="Код", max_length=32, required=False)
    duration_years = forms.IntegerField(label="Длительность (лет)", min_value=1, max_value=12, initial=4)

    def __init__(self, *args, **kwargs):
        university = kwargs.pop("university", None)
        super().__init__(*args, **kwargs)
        qs = Faculty.objects.all()
        if university:
            qs = qs.filter(university=university)
        self.fields["faculty"].queryset = qs.order_by("name")

    def clean_name(self):
        name = self.cleaned_data["name"].strip()
        if not name:
            raise ValidationError("Укажите название.")
        return name

    def save(self):
        data = self.cleaned_data
        return Program.objects.create(
            faculty=data["faculty"],
            name=data["name"],
            code=data.get("code") or "",
            duration_years=data.get("duration_years") or 4,
        )