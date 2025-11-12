from main.utils.menu import get_menu_buttons
from django.shortcuts import render
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ..models import Person, Student, GroupNotification
from django.contrib.auth import login
from django.contrib.auth import login, get_user_model
from django.contrib.auth import authenticate


def index(request):
    """Главная страница"""

    #menu_buttons = get_menu_buttons("University Moderator 3lvl")
    menu_buttons = get_menu_buttons("Headman")
    student = Student.objects.filter(pk=2).first()
    person = student.person
    group = person.student.student_group

    notif_list = list(
        GroupNotification.objects
        .filter(university=person.student.university, group=group)
        .select_related("sender")
        .order_by("-created_at")[:5]
    )
    context = {
        "menu_buttons": menu_buttons,
        "notif_list": notif_list,
    }

    return render(request, 'main/main.html', context)