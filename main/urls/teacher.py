from django.urls import path
from .. import views

teacher_patterns = [
    path('teacher_schedule/', views.teacher_schedule_view, name='teacher_schedule_view'),
    path('teacher_subjects/', views.teacher_subjects_view, name='teacher_subjects_view'),
    path('teacher_workingoff/', views.teacher_working_off_view, name='teacher_working_off_view'),
    path('teacher_request/', views.teacher_request_form, name='teacher_request_form'),
    path('teacher_make_alert/', views.teacher_make_alert_form, name='teacher_make_alert_form'),
]