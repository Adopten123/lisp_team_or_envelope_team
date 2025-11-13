from django import forms
from django.core.exceptions import ValidationError
from ..models import AdmissionRequest

class AdmissionRequestForm(forms.ModelForm):
    class Meta:
        model = AdmissionRequest
        fields = [
            'last_name', 'first_name', 'middle_name', 'email', 'phone',
            'desired_program', 'study_form', 'previous_education', 'comments'
        ]
        labels = {
            'last_name': 'Фамилия*',
            'first_name': 'Имя*',
            'middle_name': 'Отчество',
            'email': 'Email*',
            'phone': 'Телефон*',
            'desired_program': 'Желаемая программа*',
            'study_form': 'Форма обучения*',
            'previous_education': 'Предыдущее образование',
            'comments': 'Комментарии',
        }
        widgets = {
            'study_form': forms.Select(attrs={'class': 'form-select'}),
            'previous_education': forms.Textarea(attrs={'rows': 3}),
            'comments': forms.Textarea(attrs={'rows': 5}),
        }

    def clean_phone(self):
        phone = self.cleaned_data['phone']
        if len(phone) < 5:
            raise ValidationError("Номер телефона слишком короткий")
        return phone

    def clean_desired_program(self):
        program = self.cleaned_data['desired_program']
        if len(program.strip()) < 3:
            raise ValidationError("Название программы должно содержать не менее 3 символов")
        return program