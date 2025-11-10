from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    """Главная страница"""

    menu_buttons = {

    }

    return render(request, 'index.html')

def university_moderation(request):
    return HttpResponse("Страница управления университетом, тут будет выдача ролей и создание кафедр")

def student_admin_list(request):
    return HttpResponse("Страница взаимодействия со студентами")

def acts_view(request):
    return HttpResponse("Страница просмотра актов университета")

def acts_moderation(request, act_slug):
    return HttpResponse(f"Страница редактирования акта университета {act_slug}")

def schedule_view(request):
    return HttpResponse("Страница создания и просмотра существующих расписаний")

def schedule_moderation(request, schedule_slug):
    return HttpResponse(f"Страница редактирования расписания группы {schedule_slug}")

def subject_view(request):
    return HttpResponse("Страница создания и просмотра существующих предметов")

def subject_moderation(request, subject_slug):
    return HttpResponse(f"Страница редактирования дисциплины {subject_slug}")

def news_view(request):
    return HttpResponse("Страница создания и просмотра существующих новостей")

def news_moderation(request, news_slug):
    return HttpResponse(f"Страница редактирования новости {news_slug}")

def group_news_view(request, group_slug):
    return HttpResponse("Страница создания и просмотра существующих новостей")

def group_news_moderation(request, group_slug, news_slug):
    return HttpResponse(f"Страница редактирования новости {news_slug}")

def request_form(request):
    return HttpResponse("Страница написания заявлений")