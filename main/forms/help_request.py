from django import forms
from django.core.exceptions import ValidationError
from ..models import HelpRequest

class HelpRequestForm(forms.Form):
    category = forms.ChoiceField(
        choices=HelpRequest.CATEGORY_CHOICES,
        label="Категория проблемы",
        help_text="Выберите категорию проблемы"
    )
    email = forms.EmailField(
        label="Email для обратной связи",
        help_text="Введите email для ответа на ваше обращение"
    )
    subject = forms.CharField(
        max_length=255,
        label="Тема обращения",
        help_text="Кратко опишите проблему"
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 5}),
        label="Подробное описание",
        help_text="Опишите проблему максимально подробно"
    )
    priority = forms.ChoiceField(
        choices=[('low', 'Низкий'), ('medium', 'Средний'), ('high', 'Высокий')],
        label="Приоритет",
        initial='medium'
    )
    is_urgent = forms.BooleanField(
        required=False,
        label="Срочная проблема",
        help_text="Отметье, если требуется ответ в течение 2 часов"
    )

    def clean_email(self):
        email = self.cleaned_data["email"]
        return email

    def clean_subject(self):
        subject = self.cleaned_data["subject"]
        if len(subject.strip()) < 5:
            raise ValidationError("Тема обращения должна содержать не менее 5 символов")
        return subject

    def save(self):
        return HelpRequest.objects.create(
            category=self.cleaned_data["category"],
            email=self.cleaned_data["email"],
            subject=self.cleaned_data["subject"],
            description=self.cleaned_data["description"],
            priority=self.cleaned_data["priority"],
            is_urgent=self.cleaned_data["is_urgent"]
        )