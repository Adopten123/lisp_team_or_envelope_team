buttons = [
    # {
    #     "id": "news_view",
    #     "icon": "🔥",
    #     "text": "Новости",
    #     "data_action": "news",
    #     "roles": {"Guest", "Applicant", "Student", "Headman", "Journalist", "Teacher", "University Moderator 1lvl",
    #               "University Moderator 2lvl", "University Moderator 3lvl"}
    # },
    {
        "id": "create_student",
        "icon": "👤",
        "text": "Зарегистрироваться",
        "data_action": "create-student",
        "roles": {"Guest"}
    },
    {
        "id": "student_schedule_view",
        "icon": "📅",
        "text": "Расписание",
        "data_action": "schedule",
        "roles": {"Student", "Headman", "Journalist"}
    },
    {
        "id": "student_grades_view",
        "icon": "📊",
        "text": "Оценки",
        "data_action": "grades",
        "roles": {"Student", "Headman", "Journalist"}
    },
    {
        "id": "student_group_view",
        "icon": "👥",
        "text": "Моя группа",
        "data_action": "group",
        "roles": {"Student", "Headman", "Journalist"}
    },
    {
        "id": "student_request_view",
        "icon": "📋",
        "text": "Заказать справку",
        "data_action": "certificate",
        "roles": {"Student", "Headman", "Journalist"}
    },
    {
        "id": "headman_group_news_view",
        "icon": "📰",
        "text": "Оповещение группе",
        "data_action": "headman_news",
        "roles": {"Headman"}
    },
    {
        "id": "journalist_news_view",
        "icon": "📰",
        "text": "Создать новость",
        "data_action": "journalist_news",
        "roles": {"Journalist", "University Moderator 1lvl",
                  "University Moderator 2lvl", "University Moderator 3lvl"}
    },
    {
        "id": "admission_request_page",
        "icon": "🗳️",
        "text": "Подать заявление на поступление",
        "data_action": "admission_request",
        "roles": {"Applicant"}
    },
    {
        "id": "applicant_chat",
        "icon": "📁",
        "text": "Чат абитуриентов",
        "data_action": "applicant_chat",
        "roles": {"Applicant"}
    },
    {
        "id": "applicant_rating",
        "icon": "📊",
        "text": "Рейтинг абитуриентов",
        "data_action": "applicant_rating",
        "roles": {"Applicant"}
    },
    {
        "id": "teacher_schedule_view",
        "icon": "📅",
        "text": "Расписание",
        "data_action": "schedule",
        "roles": {"Teacher", "University Moderator 1lvl",
                  "University Moderator 2lvl", "University Moderator 3lvl"}
    },
    {
        "id": "teacher_subjects_view",
        "icon": "📁",
        "text": "Мои дисциплины",
        "data_action": "subjects",
        "roles": {"Teacher", "University Moderator 1lvl",
                  "University Moderator 2lvl", "University Moderator 3lvl"}
    },
    {
        "id": "teacher_working_off_view",
        "icon": "📓",
        "text": "Отработки",
        "data_action": "working_off",
        "roles": {"Teacher", "University Moderator 1lvl",
                  "University Moderator 2lvl", "University Moderator 3lvl"}
    },
    {
        "id": "teacher_request_form",
        "icon": "📋",
        "text": "Заказать справку",
        "data_action": "certificate_teacher",
        "roles": {"Teacher", "University Moderator 1lvl",
                  "University Moderator 2lvl", "University Moderator 3lvl"}
    },
    {
        "id": "teacher_make_alert_form",
        "icon": "📢",
        "text": "Оповестить о паре",
        "data_action": "make_alert_teacher",
        "roles": {"Teacher", "University Moderator 1lvl",
                  "University Moderator 2lvl", "University Moderator 3lvl"}
    },
    {
        "id": "moderation_staff",
        "icon": "💼",
        "text": "Меню персонала",
        "data_action": "staff_menu",
        "roles": {"University Moderator 2lvl", "University Moderator 3lvl"}
    },
    {
        "id": "moderation_university",
        "icon": "🏫",
        "text": "Меню университета",
        "data_action": "staff_menu",
        "roles": {"University Moderator 2lvl", "University Moderator 3lvl"}
    },
    {
        "id": "moderation_schedules",
        "icon": "📅",
        "text": "Меню расписания",
        "data_action": "schedule_menu",
        "roles": {"University Moderator 1lvl",
                  "University Moderator 2lvl", "University Moderator 3lvl"}
    },
    {
        "id": "moderation_subjects",
        "icon": "📦",
        "text": "Меню дисциплин",
        "data_action": "subject_menu",
        "roles": {"University Moderator 1lvl",
                  "University Moderator 2lvl", "University Moderator 3lvl"}
    },
    {
        "id": "moderation_requests",
        "icon": "📑",
        "text": "Обработка справок",
        "data_action": "request_menu",
        "roles": {"University Moderator 1lvl",
                  "University Moderator 2lvl", "University Moderator 3lvl"}
    },
    {
        "id": "moderation_acts",
        "icon": "🗂️",
        "text": "Меню актов",
        "data_action": "request_menu",
        "roles": {"University Moderator 1lvl",
                  "University Moderator 2lvl", "University Moderator 3lvl"}
    },
]