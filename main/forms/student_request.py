from django import forms
from django.core.exceptions import ValidationError
from main.models import StudentRequest
import json

class StudentRequestCreateForm(forms.ModelForm):
    payload_json_str = forms.CharField(
        label="Детали (JSON, опционально)",
        required=False,
        widget=forms.Textarea(attrs={"rows": 4, "placeholder": '{"to":"деканат","copies":1}'})
    )

    class Meta:
        model = StudentRequest
        fields = ["type"]
        labels = {"type": "Тип заявления"}

    def clean_payload_json_str(self):
        s = self.cleaned_data.get("payload_json_str", "").strip()
        if not s:
            return {}
        try:
            data = json.loads(s)
            if not isinstance(data, dict):
                raise ValidationError("JSON должен быть объектом ({}).")
            return data
        except Exception as e:
            raise ValidationError(f"Некорректный JSON: {e}")

    def build_payload(self):
        return self.cleaned_data.get("payload_json_str") or {}