from django import forms
from django.utils import timezone
from main.models import GroupNotification, StudentRole, StudentGroup

class HeadmanNotificationForm(forms.ModelForm):
    class Meta:
        model = GroupNotification
        fields = ("icon", "text")
        widgets = {
            "icon": forms.TextInput(
                attrs={
                    "class": "ui-input",
                    "placeholder": "Например: 🔔",
                    "maxlength": "4",
                }
            ),
            "text": forms.Textarea(
                attrs={
                    "class": "ui-textarea",
                    "placeholder": "Текст оповещения для группы...",
                    "rows": 4,
                }
            ),
        }


class TeacherNotificationForm(forms.ModelForm):
    group = forms.ModelChoiceField(
        queryset=StudentGroup.objects.none(),
        label="Группа",
        widget=forms.Select(attrs={"class": "ui-select"}),
    )

    class Meta:
        model = GroupNotification
        fields = ("icon", "group", "text")
        widgets = {
            "icon": forms.TextInput(
                attrs={
                    "class": "ui-input",
                    "placeholder": "Например: 📢",
                    "maxlength": "4",
                }
            ),
            "text": forms.Textarea(
                attrs={
                    "class": "ui-textarea",
                    "placeholder": "Сообщение для выбранной группы...",
                    "rows": 4,
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        university = kwargs.pop("university", None)
        super().__init__(*args, **kwargs)
        if university is not None:
            self.fields["group"].queryset = StudentGroup.objects.filter(
                university=university
            )
        else:
            self.fields["group"].queryset = StudentGroup.objects.all()