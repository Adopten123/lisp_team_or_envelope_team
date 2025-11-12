from django import forms
from django.contrib.admin.widgets import FilteredSelectMultiple

from main.models import (
    ScheduleSlot, ScheduleException,
    Teaching, StudentGroup,
    University
)

class ScheduleSlotForm(forms.ModelForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=StudentGroup.objects.none(),
        required=False,
        widget=FilteredSelectMultiple(verbose_name="Группы", is_stacked=False),
        label="Группы",
    )

    class Meta:
        model = ScheduleSlot
        fields = [
            "university", "teaching", "groups",
            "weekday", "start_time", "end_time", "week_parity",
            "start_date", "end_date",
            "building", "room", "note",
        ]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
            "end_date": forms.DateInput(attrs={"type": "date"}),
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
            "note": forms.TextInput(attrs={"placeholder": "Например: практика"}),
        }

    def __init__(self, *args, university: University | None = None, group: StudentGroup | None = None, **kwargs):
        super().__init__(*args, **kwargs)

        if university:
            self.fields["university"].initial = university
            self.fields["university"].disabled = True

            self.fields["teaching"].queryset = (
                Teaching.objects
                .filter(teacher__university=university)
                .select_related("curriculum__discipline", "teacher__person")
                .order_by("curriculum__discipline__title")
            )

            self.fields["groups"].queryset = (
                StudentGroup.objects
                .filter(university=university)
                .order_by("name")
            )

        if group and not self.is_bound:
            self.fields["groups"].initial = [group.pk]

    class Media:
        css = {"all": ("admin/css/widgets.css",)}
        js = (
            "admin/js/core.js",
            "admin/js/SelectBox.js",
            "admin/js/SelectFilter2.js",
        )

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
            "new_note": forms.TextInput(attrs={"placeholder": "Причина, комментарий…"}),
        }

    def __init__(self, *args, university: University | None = None, group: StudentGroup | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        qs = ScheduleSlot.objects.all()
        if university:
            qs = qs.filter(university=university)
        if group:
            qs = qs.filter(Q(groups=group) | Q(teaching__group=group))

        self.fields["slot"].queryset = qs.select_related(
            "teaching__curriculum__discipline", "teaching__teacher__person"
        ).order_by("weekday", "start_time")