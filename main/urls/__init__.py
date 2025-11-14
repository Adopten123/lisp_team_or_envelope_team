from django.urls import path
from django.conf.urls import handler400, handler403, handler404, handler500

from .public import public_patterns
from .news import news_patterns
from .student import student_patterns
from .teacher import teacher_patterns
from .moderation import moderation_patterns
from .applicant import applicant_patterns
urlpatterns = []
urlpatterns += public_patterns
urlpatterns += news_patterns
urlpatterns += student_patterns
urlpatterns += teacher_patterns
urlpatterns += moderation_patterns
urlpatterns += applicant_patterns
