# urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('api/max-auth/', views.max_auth_view, name='max_auth'),
    path('unsupported-platform/', views.unsupported_platform_view, name='unsupported_platform'),
    path('create_student/', views.create_student_view, name='create_student')
]