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