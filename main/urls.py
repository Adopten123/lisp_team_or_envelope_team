# main/urls.py
from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('university_moderation/', views.university_moderation, name='university_moderation'),
    path('student_list/', views.student_admin_list, name='student_admin_list'),
    path('acts/', views.acts_view, name='acts_view'),
    path('acts/<slug:act_slug>/', views.acts_moderation, name='acts_moderation'),
    path('schedule/', views.schedule_view, name='schedule_view'),
    path('schedule/<slug:schedule_slug>/', views.schedule_moderation, name='schedule_moderation'),
    path('subject/', views.subject_view, name='subject_view'),
    path('subject/<slug:subject_slug>/', views.subject_moderation, name='subject_moderation'),
    path('news/', views.subject_view, name='news_view'),
    path('news/<slug:news_slug>/', views.news_moderation, name='news_moderation'),
    path('news/<slug:group_slug>', views.group_news_view, name='group_news_view'),
    path('news/<slug:group_slug>/<slug:news_slug>/', views.group_news_moderation, name='group_news_moderation'),
    path('request/', views.request_form, name='request_form'),

]
