from django.http import HttpResponse

def student_schedule_view(request):
    return HttpResponse("Страница просмотра расписания студентами")

def student_grades_view(request):
    return HttpResponse("Страница просмотра оценок")

def student_group_view(request):
    return HttpResponse("Страница просмотра группы")

def student_request_view(request):
    return HttpResponse("Страница просмотра справок")