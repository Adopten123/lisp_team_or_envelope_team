from django.urls import path
from .. import views

moderation_patterns = [
    path('moderation_staff/', views.moderation_staff, name='moderation_staff'),
    path('moderation_university/', views.moderation_university, name='moderation_university'),

    path('moderation_schedule/', views.moderation_schedules, name='moderation_schedules'),
    path('moderation_schedule/slot/new/', views.moderation_schedule_slot_create, name='schedule_slot_create'),
    path('moderation_schedule/exception/new/', views.moderation_schedule_exception_create, name='schedule_exception_create'),

    path('moderation_subject/', views.moderation_subjects, name='moderation_subjects'),

    path('moderation_subject/disciplines/', views.moderation_disciplines_list, name='disciplines_list'),
    path('moderation_subject/disciplines/<int:pk>/edit/', views.moderation_discipline_edit, name='discipline_edit'),
    path('moderation_subject/disciplines/<int:pk>/delete/', views.moderation_discipline_delete, name='discipline_delete'),

    path('moderation_subject/curriculum/', views.moderation_curriculum_list, name='curriculum_list'),
    path('moderation_subject/curriculum/<int:pk>/edit/', views.moderation_curriculum_edit, name='curriculum_edit'),
    path('moderation_subject/curriculum/<int:pk>/delete/', views.moderation_curriculum_delete, name='curriculum_delete'),

    path('moderation_subject/teaching/', views.moderation_teaching_list, name='teaching_list'),
    path('moderation_subject/teaching/<int:pk>/edit/', views.moderation_teaching_edit, name='teaching_edit'),
    path('moderation_subject/teaching/<int:pk>/delete/', views.moderation_teaching_delete, name='teaching_delete'),

    path('moderation_requests/', views.moderation_requests, name='moderation_requests'),
    path('moderation_acts/', views.moderation_acts, name='moderation_acts'),

    path('student_list/', views.student_admin_list, name='student_admin_list'),
]