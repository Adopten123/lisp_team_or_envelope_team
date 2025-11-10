from django.http import HttpResponse
from django.shortcuts import render
from main.utils.menu import get_menu_buttons

def index(request):
    """Главная страница"""

    menu_buttons = get_menu_buttons("University Moderator 1lvl")

    context = {
        "menu_buttons": menu_buttons,
    }

    return render(request, 'main/main.html', context)

def news_view(request):
    return HttpResponse("Страница создания и просмотра существующих новостей")

def student_schedule_view(request):
    return HttpResponse("Страница просмотра расписания студентами")

def student_grades_view(request):
    return HttpResponse("Страница просмотра оценок")

def student_group_view(request):
    return HttpResponse("Страница просмотра группы")

def student_request_view(request):
    return HttpResponse("Страница просмотра справок")

def headman_group_news_view(request):
    return HttpResponse("Страница создания и просмотра существующих новостей")

def journalist_news_view(request):
    return HttpResponse("Страница создания новостей журналистами")

def teacher_schedule_view(request):
    return HttpResponse("Страница расписания преподавателя")

def teacher_subject_view(request):
    return HttpResponse("Страница просмотра существующих предметов преподавателя")

def teacher_working_off_view(request):
    return HttpResponse("Страница отработок преподавателя")

def teacher_request_form(request):
    return HttpResponse("Страница написания заявлений")

def teacher_make_alert_form(request):
    return HttpResponse("Страница создания оповещения о паре учителем")

def moderation_staff(request):
    return HttpResponse("Страница взаимодействия с персоналом университета")

def moderation_university(request):
    return HttpResponse("Страница управления университетом, тут будет выдача ролей и создание кафедр")

def moderation_schedules(request):
    return HttpResponse(f"Страница редактирования расписания групп")

def moderation_subjects(request):
    return HttpResponse(f"Страница редактирования дисциплин")

def moderation_requests(request):
    return HttpResponse("Страница обработки справок")

def moderation_acts(request):
    return HttpResponse(f"Страница редактирования актов университета")

def applicant_admission_request(request):
    return HttpResponse("Страница подачи заявления на поступление")

def applicant_chat(request):
    return HttpResponse("Страница чата абитуриентов")

def applicant_rating(request):
    return HttpResponse("Страница рейтинга абитуриентов")
"""
Пока что не трогать то, что ниже
"""
def acts_view(request):
    return HttpResponse("Страница просмотра актов университета")

def news_moderation(request, news_slug):
    return HttpResponse(f"Страница редактирования новости {news_slug}")

def group_news_moderation(request, group_slug, news_slug):
    return HttpResponse(f"Страница редактирования новости {news_slug}")

def student_admin_list(request):
    return HttpResponse("Страница взаимодействия со студентами")