from main.utils.menu import get_menu_buttons
from django.shortcuts import render
from ..models import Student, GroupNotification


def index(request):
    """Главная страница"""

    """
    Guest - гость
    Applicant - абитуриент
    Student - студент
    Headman - староста 
    Journalist - журналист
    Teacher - учитель
    University Moderator 1lvl - модератор 1 уровня
    University Moderator 2lvl - модератор 2 уровня
    University Moderator 3lvl - модератор 3 уровня
    """
    menu_buttons = get_menu_buttons("University Moderator 3lvl")

    student = Student.objects.filter(pk=1).first()
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
        "person": person,
    }

    return render(request, 'main/main.html', context)