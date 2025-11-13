from django.urls import path
from .. import views

applicant_patterns = [
    path('admission_request/', views.admission_request_page, name='admission_request_page'),
    path('applicant_chat/', views.applicant_chat_working_off_view, name='applicant_chat'),
    path('applicant_rating/', views.applicant_rating, name='applicant_rating'),
]