from django import forms
from django.core.exceptions import ValidationError
from ..models import ApplicationRequest

class AdmissionRequestForm(forms.Form):
    last_name = forms.CharField(max_length=128, label="Фамилия*")
    first_name = forms.CharField(max_length=128, label="Имя*")
    middle_name = forms.CharField(max_length=128, label="Отчество", required=False)
    email = forms.EmailField(label="Email*")
    phone = forms.CharField(max_length=20, label="Телефон*")
    desired_program = forms.CharField(max_length=255, label="Желаемая программа*")
    study_form = forms.ChoiceField(
        choices=ApplicationRequest.STUDY_FORM_CHOICES,  # Используем из новой модели
        label="Форма обучения*",
        initial='full_time'
    )
    previous_education = forms.CharField(
        max_length=255,
        label="Предыдущее образование",
        required=False,
        widget=forms.Textarea(attrs={'rows': 3})
    )
    comments = forms.CharField(
        label="Комментарии",
        required=False,
        widget=forms.Textarea(attrs={'rows': 5})
    )

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

    def save(self):
        """Создает объект ApplicationRequest с данными из формы"""
        return ApplicationRequest.objects.create(  # Изменили на ApplicationRequest
            last_name=self.cleaned_data['last_name'],
            first_name=self.cleaned_data['first_name'],
            middle_name=self.cleaned_data['middle_name'],
            email=self.cleaned_data['email'],
            phone=self.cleaned_data['phone'],
            desired_program=self.cleaned_data['desired_program'],
            study_form=self.cleaned_data['study_form'],
            previous_education=self.cleaned_data['previous_education'],
            comments=self.cleaned_data['comments'],
        )