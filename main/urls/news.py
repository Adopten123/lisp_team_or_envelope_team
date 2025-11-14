from django.urls import path
from .. import views

news_patterns = [
    path('news/', views.news_view, name='news_view'),
    path('news/<int:news_id>/', views.news_detail_view, name='news_detail'),
    path('news/<slug:news_slug>/', views.news_moderation, name='news_moderation'),
    path('news/<slug:group_slug>/<slug:news_slug>/', views.group_news_moderation, name='group_news_moderation'),
]