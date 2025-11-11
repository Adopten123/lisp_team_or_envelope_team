from django.http import HttpResponse

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