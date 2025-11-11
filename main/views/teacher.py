from django.http import HttpResponse

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