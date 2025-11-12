from django import forms
from main.models import TeacherRequest

class TeacherRequestCreateForm(forms.ModelForm):
    class Meta:
        model = TeacherRequest
        fields = ["type"]
        widgets = {
            "type": forms.Select(attrs={"class": "form-select"}),
        }
