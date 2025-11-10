# main/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('news/', views.news_view, name='news_view'),
    path('schedule/', views.student_schedule_view, name='student_schedule_view'),
    path('grades/', views.student_grades_view, name='student_grades_view'),
    path('group/', views.student_group_view, name='student_group_view'),
    path('student_request/', views.student_request_view, name='student_request_view'),
    path('group_news/', views.headman_group_news_view, name='headman_group_news_view'),
    path('create_news/', views.journalist_news_view, name='journalist_news_view'),
    path('teacher_schedule/', views.teacher_schedule_view, name='teacher_schedule_view'),
    path('teacher_subjects/', views.teacher_subject_view, name='teacher_subject_view'),
    path('teacher_workingoff/', views.teacher_working_off_view, name='teacher_working_off_view'),
    path('teacher_request/', views.teacher_request_form, name='teacher_request_form'),
    path('teacher_make_alert/', views.teacher_make_alert_form, name='teacher_make_alert_form'),
    path('university_moderation/', views.university_moderation, name='university_moderation'),
    path('student_list/', views.student_admin_list, name='student_admin_list'),
    path('acts/', views.acts_view, name='acts_view'),
    path('acts/<slug:act_slug>/', views.acts_moderation, name='acts_moderation'),
    path('schedule/<slug:schedule_slug>/', views.schedule_moderation, name='schedule_moderation'),
    path('subject/<slug:subject_slug>/', views.subject_moderation, name='subject_moderation'),
    path('news/<slug:news_slug>/', views.news_moderation, name='news_moderation'),
    path('news/<slug:group_slug>/<slug:news_slug>/', views.group_news_moderation, name='group_news_moderation'),

]
