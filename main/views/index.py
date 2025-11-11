from main.utils.menu import get_menu_buttons
from django.shortcuts import render

def index(request):
    """Главная страница"""

    menu_buttons = get_menu_buttons("University Moderator 3lvl")

    context = {
        "menu_buttons": menu_buttons,
    }

    return render(request, 'main/main.html', context)