from django.shortcuts import render

from main.models import Person
from main.utils.menu import get_menu_buttons

def profile_view(request):
    """Страница профиля пользователя"""
    try:
        # Получаем объект Person, связанный с текущим пользователем
        user = request.user
        person = user.person

        # Получаем роль пользователя для меню
        role_name = "Student"  # значение по умолчанию
        if person.role:
            role_name = person.role.name

        # Проверяем, есть ли связанные объекты Student или Teacher
        student = getattr(person, 'student', None)
        teacher = getattr(person, 'teacher', None)
        applicant = getattr(person, 'applicant', None)

        context = {
            'person': person,
            'student': student,
            'teacher': teacher,
            'applicant': applicant,
            'menu_buttons': get_menu_buttons(role_name),
        }

    except:
        # Если объект Person не найден для текущего пользователя
        context = {
            'person': None,
            'error': f'Профиль не найден',
            'menu_buttons': get_menu_buttons("Student"),  # роль по умолчанию
        }

    return render(request, 'main/profile/profile.html', context)