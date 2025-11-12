from django import forms
from main.models import ScheduleSlot, ScheduleException, Teaching, StudentGroup

class ScheduleSlotForm(forms.ModelForm):
    class Meta:
        model = ScheduleSlot
        fields = [
            "university", "teaching", "groups",
            "weekday", "start_time", "end_time", "week_parity",
            "start_date", "end_date",
            "building", "room", "note",
        ]
        widgets = {
            "note": forms.TextInput(attrs={"placeholder": "Например: практическое занятие"}),
            "start_date": forms.DateInput(attrs={"type": "date", "class": "ui-input"}),
            "end_date": forms.DateInput(attrs={"type": "date", "class": "ui-input"}),
            "start_time": forms.TimeInput(attrs={"type": "time", "class": "ui-input"}),
            "end_time": forms.TimeInput(attrs={"type": "time", "class": "ui-input"}),
            "weekday": forms.Select(attrs={"class": "ui-select"}),
            "week_parity": forms.Select(attrs={"class": "ui-select"}),
            "building": forms.TextInput(attrs={"class": "ui-input"}),
            "room": forms.TextInput(attrs={"class": "ui-input"}),
        }

    def __init__(self, *args, university=None, **kwargs):
        super().__init__(*args, **kwargs)

        if university:
            self.fields["university"].initial = university
            self.fields["university"].disabled = True
            self.fields["teaching"].queryset = Teaching.objects.filter(teacher__university=university)

        if not university and getattr(self.instance, "teaching_id", None):
            uni2 = self.instance.teaching.teacher.university
            self.fields["teaching"].queryset = Teaching.objects.filter(teacher__university=uni2)
            if not self.fields["university"].initial:
                self.fields["university"].initial = uni2
                self.fields["university"].disabled = True

        uni_for_groups = university or (getattr(self.instance, "teaching", None) and self.instance.teaching.teacher.university)
        if uni_for_groups:
            self.fields["groups"].queryset = StudentGroup.objects.filter(university=uni_for_groups).order_by("name")
        else:
            self.fields["groups"].queryset = StudentGroup.objects.all().order_by("name")

        self.fields["teaching"].widget.attrs.update({"class": "ui-select"})
        self.fields["groups"].widget = forms.SelectMultiple(attrs={"size": 10, "class": "ui-multiselect"})

class ScheduleExceptionForm(forms.ModelForm):
    class Meta:
        model = ScheduleException
        fields = [
            "slot", "date", "action",
            "new_date", "new_start_time", "new_end_time",
            "new_building", "new_room", "new_note",
        ]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "new_date": forms.DateInput(attrs={"type": "date"}),
            "new_start_time": forms.TimeInput(attrs={"type": "time"}),
            "new_end_time": forms.TimeInput(attrs={"type": "time"}),
        }

    def __init__(self, *args, university=None, **kwargs):
        super().__init__(*args, **kwargs)
        if university:
            self.fields["slot"].queryset = (
                ScheduleSlot.objects.filter(university=university)
                .select_related("teaching__curriculum__discipline")
                .order_by("weekday", "start_time")
            )