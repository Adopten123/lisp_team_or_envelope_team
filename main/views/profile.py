from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from ..models import Person, Student, Teacher, Applicant, StudentGroup, University, Faculty


def get_menu_buttons(role_name):
    """Функция для получения меню в зависимости от роли"""
    if role_name == "Student":
        return [
            {'id': 'schedule', 'icon': '📅', 'text': 'Расписание'},
            {'id': 'grades', 'icon': '📊', 'text': 'Оценки'},
            {'id': 'studentRequest', 'icon': '📝', 'text': 'Заказать справку'},
            {'id': 'courses', 'icon': '👥', 'text': 'Моя группа'},
        ]
    elif role_name == "Teacher":
        return [
            {'id': 'schedule', 'icon': '📅', 'text': 'Расписание'},
            {'id': 'journal', 'icon': '📖', 'text': 'Журнал'},
            {'id': 'materials', 'icon': '📝', 'text': 'Материалы'},
            {'id': 'students', 'icon': '👥', 'text': 'Студенты'},
        ]
    else:  # Applicant или Guest
        return [
            {'id': 'application', 'icon': '📄', 'text': 'Подать заявление'},
            {'id': 'info', 'icon': '🏫', 'text': 'О вузе'},
        ]


def profile_view(request):
    """Страница профиля пользователя - упрощенная для тестирования"""

    # Выбор роли для тестирования через параметр URL
    debug_role = request.GET.get('role', 'student')  # ?role=teacher или ?role=applicant

    try:
        # Пробуем получить реальные данные
        person = Person.objects.filter(pk=1).first()
        if person:
            student = getattr(person, 'student', None)
            teacher = getattr(person, 'teacher', None)
            applicant = getattr(person, 'applicant', None)

            role_name = person.role.name if person.role else "Student"
            context = {
                'person': person,
                'student': student,
                'teacher': teacher,
                'applicant': applicant,
                'menu_buttons': get_menu_buttons(role_name),
            }
        else:
            # Если нет реальных данных - создаем фиктивные
            if debug_role == 'teacher':
                context = create_mock_teacher_context()
            elif debug_role == 'applicant':
                context = create_mock_applicant_context()
            else:
                context = create_mock_student_context()

    except Exception as e:
        # Если что-то пошло не так - создаем фиктивные данные
        context = create_mock_student_context()

    return render(request, 'main/profile/profile.html', context)


def create_mock_student_context():
    """Создает фиктивные данные студента для тестирования"""

    class MockUser:
        username = "ivanov_i"
        email = "ivanov@university.ru"

        def get_full_name(self):
            return "Иванов Иван Иванович"

    class MockPerson:
        user = MockUser()
        last_name = "Иванов"
        first_name = "Иван"
        middle_name = "Иванович"
        email = "ivanov@university.ru"
        phone = "+7 (912) 345-67-89"
        role = type('MockRole', (), {'name': 'Student'})()

    class MockUniversity:
        name = "Национальный исследовательский университет ИТМО"

    class MockFaculty:
        name = "Факультет информационных технологий и программирования"

    class MockStudentGroup:
        name = "К3140"
        faculty = MockFaculty()

    class MockStudent:
        university = MockUniversity()
        student_group = MockStudentGroup()
        student_id = "12345678"
        current_year = 2
        admission_year = 2023

    return {
        'person': MockPerson(),
        'student': MockStudent(),
        'teacher': None,
        'applicant': None,
        'menu_buttons': get_menu_buttons("Student"),
    }


def create_mock_teacher_context():
    """Создает фиктивные данные преподавателя для тестирования"""

    class MockUser:
        username = "petrova_a"
        email = "petrova@university.ru"

        def get_full_name(self):
            return "Петрова Анна Сергеевна"

    class MockPerson:
        user = MockUser()
        last_name = "Петрова"
        first_name = "Анна"
        middle_name = "Сергеевна"
        email = "petrova@university.ru"
        phone = "+7 (923) 456-78-90"
        role = type('MockRole', (), {'name': 'Teacher'})()

    class MockUniversity:
        name = "Национальный исследовательский университет ИТМО"

    class MockTeacher:
        academic_title = "Доцент"
        department = "Кафедра компьютерных технологий"
        university = MockUniversity()

    return {
        'person': MockPerson(),
        'student': None,
        'teacher': MockTeacher(),
        'applicant': None,
        'menu_buttons': get_menu_buttons("Teacher"),
    }


def create_mock_applicant_context():
    """Создает фиктивные данные абитуриента для тестирования"""

    class MockUser:
        username = "sidorov_e"
        email = "sidorov@example.ru"

        def get_full_name(self):
            return "Сидоров Егор Дмитриевич"

    class MockPerson:
        user = MockUser()
        last_name = "Сидоров"
        first_name = "Егор"
        middle_name = "Дмитриевич"
        email = "sidorov@example.ru"
        phone = "+7 (934) 567-89-01"
        role = type('MockRole', (), {'name': 'Applicant'})()

    class MockApplicant:
        birth_date = "2005-03-15"
        passport_number = "4512 123456"
        address = "г. Санкт-Петербург, ул. Примерная, д. 10, кв. 25"
        school_name = "Гимназия №157 им. принцессы Е.М. Ольденбургской"
        graduation_year = 2024
        linked_student = None

    return {
        'person': MockPerson(),
        'student': None,
        'teacher': None,
        'applicant': MockApplicant(),
        'menu_buttons': get_menu_buttons("Applicant"),
    }