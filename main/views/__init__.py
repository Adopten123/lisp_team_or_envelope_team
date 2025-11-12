from .news import news_view, news_detail_view
from .index import index
from .student import student_schedule_view, student_grades_view, student_group_view, student_request_view
from .headman import headman_group_news_view
from .journalist import journalist_news_view

from .teacher import (
    teacher_schedule_view,
    teacher_subjects_view,
    teacher_working_off_view,
    teacher_request_form,
    teacher_make_alert_form)

from .moderation import (
    moderation_staff,
    moderation_university,
    moderation_schedules,
    moderation_subjects,
    moderation_requests,
    moderation_acts
)

from .applicant import applicant_chat, applicant_rating

from .in_process import acts_view, news_moderation, group_news_moderation, student_admin_list

from .profile import profile_view

from .help import help_page

from .admission_request import admission_request_page

from .moderation_subject import (
    moderation_disciplines_list, moderation_discipline_edit, moderation_discipline_delete,
    moderation_curriculum_list, moderation_curriculum_edit, moderation_curriculum_delete,
    moderation_teaching_list, moderation_teaching_edit, moderation_teaching_delete,
)

from .moderation_schedule import (
    moderation_schedule_slot_create,
    moderation_schedule_exception_create,
)

"""
Полезные импорты

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.db import models
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from main.models import Person, NewsPost
from main.utils.menu import get_menu_buttons

"""