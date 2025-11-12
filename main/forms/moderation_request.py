from django import forms

STUDENT_ACTIONS = [
    ("in_progress", "В работу"),
    ("approved", "Одобрить"),
    ("rejected", "Отклонить"),
    ("issued", "Выдано"),
]
TEACHER_ACTIONS = [
    ("in_review", "На рассмотрение"),
    ("approved", "Одобрить"),
    ("rejected", "Отклонить"),
    ("issued", "Выдано"),
]

class ModerationActionForm(forms.Form):
    """Форма смены статуса одной записи (универсальная для Student/Teacher)."""
    model = forms.ChoiceField(choices=[("student", "student"), ("teacher", "teacher")], widget=forms.HiddenInput)
    obj_id = forms.IntegerField(widget=forms.HiddenInput)
    new_status = forms.CharField(widget=forms.HiddenInput)

class FilterForm(forms.Form):
    """Фильтры списка."""
    source = forms.ChoiceField(
        choices=[("", "Все источники"), ("student", "Студенты"), ("teacher", "Преподаватели")],
        required=False
    )
    req_type = forms.CharField(required=False)  # значение перечисления модели
    status = forms.CharField(required=False)
    q = forms.CharField(required=False)
    date_from = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))
    date_to = forms.DateField(required=False, widget=forms.DateInput(attrs={"type": "date"}))