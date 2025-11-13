from django.urls import path
from .. import views

public_patterns = [
    path('', views.index, name='index'),
    path('profile/', views.profile_view, name='profile_view'),
    path('help/', views.help_page, name='help_page'),
    path('acts/', views.acts_view, name='acts_view'),
]