from django import forms
from django.utils import timezone
from main.models import GroupNotification, StudentRole, StudentGroup

class HeadmanNotificationForm(forms.ModelForm):
    class Meta:
        model = GroupNotification
        fields = ("icon", "text")
        widgets = {
            "icon": forms.TextInput(attrs={"placeholder": "Напр. 📝", "class": "ui-input"}),
            "text": forms.Textarea(attrs={"rows": 3, "placeholder": "Сообщение для группы...", "class": "ui-textarea"}),
        }

    def __init__(self, *args, **kwargs):
        # ожидаем extra аргументы: university, group, sender
        self.university = kwargs.pop("university")
        self.group = kwargs.pop("group")
        self.sender = kwargs.pop("sender")
        super().__init__(*args, **kwargs)

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.university = self.university
        obj.group = self.group
        obj.sender = self.sender
        if commit:
            obj.save()
        return obj


class TeacherNotificationForm(forms.ModelForm):
    group = forms.ModelChoiceField(
        label="Группа", queryset=StudentGroup.objects.none(),
        widget=forms.Select(attrs={"class": "ui-select"})
    )

    class Meta:
        model = GroupNotification
        fields = ("group", "icon", "text")
        widgets = {
            "icon": forms.TextInput(attrs={"placeholder": "Напр. 📅", "class": "ui-input"}),
            "text": forms.Textarea(attrs={"rows": 3, "placeholder": "Сообщение для выбранной группы...", "class": "ui-textarea"}),
        }

    def __init__(self, *args, **kwargs):
        teacher = kwargs.pop("teacher")
        university = kwargs.pop("university")
        super().__init__(*args, **kwargs)

        # группы, которые ведёт преподаватель
        qs = StudentGroup.objects.filter(
            teachings__teacher=teacher,
            university=university,
        ).distinct().order_by("name")
        self.fields["group"].queryset = qs