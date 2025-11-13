from main.utils.menu import get_menu_buttons
from django.shortcuts import render
from django.conf import settings
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ..models import Person
from django.contrib.auth import login
from django.contrib.auth import login, get_user_model
from django.contrib.auth import authenticate


def index(request):
    """Главная страница"""

    #menu_buttons = get_menu_buttons("University Moderator 3lvl")
    menu_buttons = get_menu_buttons("Applicant")
    context = {
        "menu_buttons": menu_buttons,
    }

    return render(request, 'main/main.html', context)