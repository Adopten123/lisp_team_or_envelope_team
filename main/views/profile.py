from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ..models import Person, Student, Teacher, Applicant, StudentGroup, University, Faculty
from ..utils.profile_buttons import get_menu_buttons
from ..utils.auth import get_current_person

def profile_view(request):
    """Страница профиля пользователя"""
    try:
        # Получаем объект Person, связанный с текущим пользователем
        person = request.user.person
        #person = Person.objects.filter(pk=1).first()

        # Получаем роль пользователя для меню
        role_name = person.role.name if person.role else "Student"

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

    except Person.DoesNotExist:
        # Если объект Person не найден для текущего пользователя
        context = {
            'person': None,
            'error': 'Профиль не найден. Обратитесь к администратору.',
            'menu_buttons': get_menu_buttons("Guest"),
        }
    except Exception as e:
        # Обработка других возможных ошибок
        context = {
            'person': None,
            'error': f'Произошла ошибка: {str(e)}',
            'menu_buttons': get_menu_buttons("Guest"),
        }

    return render(request, 'main/profile/profile.html', context)