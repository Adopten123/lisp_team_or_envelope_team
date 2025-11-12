# main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('news/', views.news_view, name='news_view'),
    path('profile/', views.profile_view, name='profile_view'),
    path('help/', views.help_page, name='help_page'),
    path('news/<int:news_id>/', views.news_detail_view, name='news_detail'),
    path('schedule/', views.student_schedule_view, name='student_schedule_view'),
    path('grades/', views.student_grades_view, name='student_grades_view'),
    path('group/', views.student_group_view, name='student_group_view'),
    path('student_request/', views.student_request_view, name='student_request_view'),
    path('group_news/', views.headman_group_news_view, name='headman_group_news_view'),
    path('create_news/', views.journalist_news_view, name='journalist_news_view'),
    path('teacher_schedule/', views.teacher_schedule_view, name='teacher_schedule_view'),
    path('teacher_subjects/', views.teacher_subjects_view, name='teacher_subjects_view'),
    path('teacher_workingoff/', views.teacher_working_off_view, name='teacher_working_off_view'),
    path('teacher_request/', views.teacher_request_form, name='teacher_request_form'),
    path('teacher_make_alert/', views.teacher_make_alert_form, name='teacher_make_alert_form'),
    path('moderation_staff/', views.moderation_staff, name='moderation_staff'),
    path('moderation_university/', views.moderation_university, name='moderation_university'),
    path('moderation_schedule/', views.moderation_schedules, name='moderation_schedules'),
    path("moderation_schedule/slot/new/", views.moderation_schedule_slot_create, name="schedule_slot_create"),
    path("moderation_schedule/exception/new/", views.moderation_schedule_exception_create, name="schedule_exception_create"),
    path('moderation_subject/', views.moderation_subjects, name='moderation_subjects'),
    path('moderation_requests/', views.moderation_requests, name='moderation_requests'),
    path('moderation_acts/', views.moderation_acts, name='moderation_acts'),
    path('admission_request/', views.applicant_admission_request, name='applicant_admission_request'),
    path('applicant_chat/', views.applicant_chat, name='applicant_chat'),
    path('applicant_rating/', views.applicant_rating, name='applicant_rating'),
    path('student_list/', views.student_admin_list, name='student_admin_list'),
    path('acts/', views.acts_view, name='acts_view'),
    path('news/<slug:news_slug>/', views.news_moderation, name='news_moderation'),
    path('news/<slug:group_slug>/<slug:news_slug>/', views.group_news_moderation, name='group_news_moderation'),

    path("moderation_subject/disciplines/", views.moderation_disciplines_list, name="disciplines_list"),
    path("moderation_subject/disciplines/<int:pk>/edit/", views.moderation_discipline_edit, name="discipline_edit"),
    path("moderation_subject/disciplines/<int:pk>/delete/", views.moderation_discipline_delete, name="discipline_delete"),

    path("moderation_subject/curriculum/", views.moderation_curriculum_list, name="curriculum_list"),
    path("moderation_subject/curriculum/<int:pk>/edit/", views.moderation_curriculum_edit, name="curriculum_edit"),
    path("moderation_subject/curriculum/<int:pk>/delete/", views.moderation_curriculum_delete, name="curriculum_delete"),

    path("moderation_subject/teaching/", views.moderation_teaching_list, name="teaching_list"),
    path("moderation_subject/teaching/<int:pk>/edit/", views.moderation_teaching_edit, name="teaching_edit"),
    path("moderation_subject/teaching/<int:pk>/delete/", views.moderation_teaching_delete, name="teaching_delete"),
]
