from django.urls import path
from .. import views

student_patterns = [
    path('schedule/', views.student_schedule_view, name='student_schedule_view'),
    path('grades/', views.student_grades_view, name='student_grades_view'),
    path('group/', views.student_group_view, name='student_group_view'),
    path('student_request/', views.student_request_view, name='student_request_view'),
    path('group_news/', views.headman_group_news_view, name='headman_group_news_view'),
    path('create_news/', views.journalist_news_view, name='journalist_news_view'),
]