from django.http import HttpResponse
from django.shortcuts import render
from main.utils.menu import get_menu_buttons

def index(request):
    """Главная страница"""

    menu_buttons = get_menu_buttons("Teacher")

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

def headman_group_news_view(request, group_slug):
    return HttpResponse("Страница создания и просмотра существующих новостей")

def journalist_news_view(request):
    return HttpResponse("Страница создания новостей журналистами")

def university_moderation(request):
    return HttpResponse("Страница управления университетом, тут будет выдача ролей и создание кафедр")

def student_admin_list(request):
    return HttpResponse("Страница взаимодействия со студентами")

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
def acts_view(request):
    return HttpResponse("Страница просмотра актов университета")

def acts_moderation(request, act_slug):
    return HttpResponse(f"Страница редактирования акта университета {act_slug}")

def schedule_moderation(request, schedule_slug):
    return HttpResponse(f"Страница редактирования расписания группы {schedule_slug}")

def subject_moderation(request, subject_slug):
    return HttpResponse(f"Страница редактирования дисциплины {subject_slug}")

def news_moderation(request, news_slug):
    return HttpResponse(f"Страница редактирования новости {news_slug}")

def group_news_moderation(request, group_slug, news_slug):
    return HttpResponse(f"Страница редактирования новости {news_slug}")